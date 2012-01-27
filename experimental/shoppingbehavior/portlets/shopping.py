from plone.portlets.interfaces import IPortletDataProvider
from zope.interface import implements
from zope.cachedescriptors.property import Lazy as lazy_property

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

    @property
    def available(self):
        if self.priced is not None and self.priced.price is not None:
            return self.priced.enabled
        return False

    @lazy_property
    def priced(self):
        return behaviors.IPriced(self.context, None)

    @property
    def price(self):
        self.priced.price

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
