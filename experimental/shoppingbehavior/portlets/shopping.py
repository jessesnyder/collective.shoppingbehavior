from plone.portlets.interfaces import IPortletDataProvider
from zope.interface import implements

from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from plone.app.portlets.portlets import base
from getpaid.core.interfaces import IPayableLineItem

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
        self.payable = IPayableLineItem(self.context)

    @property
    def available(self):
        return self.status.isPriceEnabled()

    def update(self):
        pass

    def price(self):
        return self.payable.cost

    def title(self):
        return self.payable.name

    def description(self):
        return self.payable.description

    def currency(self):
        return u"$"

    render = ViewPageTemplateFile('shopping.pt')


class AddForm(base.NullAddForm):

    def create(self):
        return Assignment()
