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
        self.status = behaviors.IPricingStatus(self.context, None)

    @property
    def available(self):
        return self.status is not None and self.status.isPriceEnabled() \
            and self.price is not None

    def update(self):
        pass

    @property
    def price(self):
        return behaviors.IPriced(self.context).price

    @property
    def title(self):
        return self.context.title

    @property
    def description(self):
        return self.context.description

    @property
    def currency(self):
        return u"$"

    render = ViewPageTemplateFile('shopping.pt')


class AddForm(base.NullAddForm):

    def create(self):
        return Assignment()
