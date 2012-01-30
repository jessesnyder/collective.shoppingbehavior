from zope.interface import alsoProvides
from zope.interface import Interface
from zope.interface import invariant, Invalid
from zope import schema
from plone.directives import form

from experimental.shoppingbehavior import _


class IPotentiallyPriced(Interface):
    """ Marker interface for content types that can have pricing enabled. This
        interface on type for which the IPriced behavior is enabled.
    """


class IPriced(form.Schema):
    """ Add a price to a content object
    """

    form.fieldset(
            'pricing',
            label=u'Pricing',
            fields=('enabled', 'price',),
        )
    enabled = schema.Bool(
        title=u'Enabled',
        description=u'Enable pricing for this item',
        default=False,
        required=False,
    )
    price = schema.Decimal(
        title=u'Price',
        description=u'The price for this item',
        required=False,
    )

    @invariant
    def priceMustBeSetIfEnabled(data):
        if data.enabled and data.price is None:
            raise Invalid(
                _(u"A price must be set in order for pricing to be enabled."))

alsoProvides(IPriced, form.IFormFieldProvider)
