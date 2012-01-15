from zope.interface import Interface, implements, alsoProvides
from zope.component import adapts, queryUtility
from zope.annotation import IAnnotations
from Acquisition import aq_inner
from zope import schema

from plone.behavior.interfaces import IBehavior
from plone.dexterity.behavior import DexterityBehaviorAssignable
from plone.directives import form
from plone.memoize import view
from Products.Five.browser import BrowserView
from Products.statusmessages.interfaces import IStatusMessage

from experimental.shoppingbehavior.config import PRICE_BEHAVIOR_KEY as KEY
from experimental.shoppingbehavior import _


class IPotentiallyPriced(Interface):
    """ Objects or classes providing this interface will support local behavior
        assignment.
    """


class IPricingStatus(Interface):

    def isPriceEnabled():
        """ Is pricing currently enabled? """

    def isPriceEnableable():
        """ Can pricing be enabled? """

    def enablePricing():
        """ Enable pricing for this object """

    def disablePricing():
        """ Disable pricing for this object """


class PricingStatus(object):
    implements(IPricingStatus)
    adapts(IPotentiallyPriced)

    behavior = 'experimental.shoppingbehavior.behaviors.IPriced'

    def __init__(self, context):
        self.context = context

    def isPriceEnableable(self):
        return not self.isPriceEnabled()

    def isPriceEnabled(self):
        annotations = IAnnotations(self.context)
        instance_behaviors = annotations.get(KEY, ())
        return self.behavior in instance_behaviors

    def enablePricing(self):
        annotations = IAnnotations(self.context)
        instance_behaviors = annotations.get(KEY, ())
        if self.behavior not in instance_behaviors:
            instance_behaviors += (self.behavior,)
        annotations[KEY] = instance_behaviors

    def disablePricing(self):
        annotations = IAnnotations(self.context)
        instance_behaviors = annotations.get(KEY, ())
        if self.behavior in instance_behaviors:
            instance_behaviors = tuple(
                [b for b in instance_behaviors if b != self.behavior])
        annotations[KEY] = instance_behaviors


class PricingStatusView(BrowserView):
    """ Configuration/utility view for enabling and disabling pricing """

    behavior_name = 'wacdl.payments.behaviors.IPriced'

    @view.memoize
    def isPriceEnableable(self):
        """ See interface definition """
        context = aq_inner(self.context)
        if not IPotentiallyPriced.providedBy(context):
            return False
        return not self.isPriceEnabled()

    @view.memoize
    def isPriceEnabled(self):
        """ See interface definition """
        context = aq_inner(self.context)
        if not IPotentiallyPriced.providedBy(context):
            return False
        config = IPricingStatus(context)
        return config.isPriceEnabled()

    def enablePricing(self):
        """ See interface definition """
        context = aq_inner(self.context)
        config = IPricingStatus(context)
        config.enablePricing()
        IStatusMessage(self.request).add(
            _(u"Pricing has been enabled for this object."),
              u"info")
        self.request.RESPONSE.redirect(context.absolute_url())
        return ''

    def disablePricing(self):
        """ See interface definition """
        context = aq_inner(self.context)
        config = IPricingStatus(context)
        config.disablePricing()
        IStatusMessage(self.request).add(
            _(u"Pricing has been disabled for this object."),
              u"info")
        self.request.RESPONSE.redirect(context.absolute_url())
        return ''


class DexterityInstanceBehaviorAssignable(DexterityBehaviorAssignable):
    """ Support per instance specification of plone.behavior behaviors
    """
    adapts(IPotentiallyPriced)

    def __init__(self, context):
        super(DexterityInstanceBehaviorAssignable, self).__init__(context)
        annotations = IAnnotations(context)
        self.instance_behaviors = annotations.get(KEY, ())

    def enumerateBehaviors(self):
        self.behaviors = self.fti.behaviors + self.instance_behaviors
        for name in self.behaviors:
            behavior = queryUtility(IBehavior, name=name)
            if behavior is not None:
                yield behavior


class IPriced(form.Schema):
    """ Add a price to a content object
    """

    form.fieldset(
            'pricing',
            label=u'Pricing',
            fields=('payable', 'price',),
        )
    price = schema.Float(
        title=u'Price',
        description=u'The price for this item',
        required=False,
    )

alsoProvides(IPriced, form.IFormFieldProvider)
