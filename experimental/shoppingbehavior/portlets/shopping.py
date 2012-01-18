from plone.portlets.interfaces import IPortletDataProvider
from zope.interface import implements

from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from plone.app.portlets.portlets import base

from experimental.shoppingbehavior import _
from experimental.shoppingbehavior import behaviors


class IShoppingPortlet(IPortletDataProvider):
    """A portlet for adding the context item to the shopping cart.
    """


class Assignment(base.Assignment):
    implements(IShoppingPortlet)

    title = _(u'label_shopping', default=u'Add to cart')


class Renderer(base.Renderer):

    def __init__(self, context, request, view, manager, data):
        base.Renderer.__init__(self, context, request, view, manager, data)
        self.status = behaviors.IPricingStatus(self.context)
        # TODO: do we need init?

    @property
    def available(self):
        return self.status.isPriceEnabled()

    def update(self):
        pass

    def price(self):
        priced = behaviors.IPriced(self.context, None)
        if priced is None:
            return 0.0
        return priced.price

    def currency(self):
        return u"$"

    render = ViewPageTemplateFile('shopping.pt')


class AddForm(base.NullAddForm):

    def create(self):
        return Assignment()
