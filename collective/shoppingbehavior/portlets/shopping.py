from plone.portlets.interfaces import IPortletDataProvider
from zope.interface import implements
from zope.cachedescriptors.property import Lazy as lazy_property

from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from Products.CMFCore.utils import getToolByName
from plone.app.portlets.portlets import base

from collective.shoppingbehavior import _
from collective.shoppingbehavior import behaviors
from collective.shoppingbehavior.shop import StdNamingPolicy
from collective.shoppingbehavior.shop import getShopper


class IAddToCartPortlet(IPortletDataProvider):
    """A portlet for adding the context item to the shopping cart.
    """


class AddToCartPortletAssignment(base.Assignment):
    implements(IAddToCartPortlet)

    title = _(u'label_addtocart', default=u'Add to cart')


class AddToCartPortletRenderer(base.Renderer):

    @property
    def available(self):
        if self.priced is not None and self.priced.pricelist:
            return self.priced.enabled
        return False

    @lazy_property
    def priced(self):
        return behaviors.IPriced(self.context, None)

    @lazy_property
    def shopper(self):
        return getShopper()

    @property
    def pricelist(self):
        return self.priced.pricelist

    @property
    def title(self):
        return self.context.title

    @property
    def description(self):
        return self.context.description

    @property
    def currency(self):
        return u"$"

    @property
    def context_is_in_cart(self):
        for namedprice in self.pricelist:
            naming = StdNamingPolicy(namedprice, self.context)
            if self.shopper.contains(naming.id()):
                return True
        return False

    render = ViewPageTemplateFile('shopping.pt')


class AddToCartPortletAddForm(base.NullAddForm):

    def create(self):
        return AddToCartPortletAssignment()


class ICartListingPortlet(IPortletDataProvider):
    """A portlet which shows what's currently in the shopping cart.
    """


class CartListingPortletAssignment(base.Assignment):
    implements(ICartListingPortlet)

    title = _(u'label_cartlisting', default=u'Shopping Cart Summary')


class CartListingPortletRenderer(base.Renderer):

    contextsWherePortletShouldNotShow = ('csb-cart-update', 'checkout')

    @property
    def available(self):
        return self._isSensibleContext() and self.shopper.size() > 0

    @lazy_property
    def shopper(self):
        return getShopper()

    def checkout(self):
        self.shopper.checkout()

    @property
    def items(self):
        contents = []
        cart_contents = self.shopper.items()
        if not cart_contents:
            return contents
        for item in cart_contents:
            data = {}
            data['item_id'] = item[0]
            data['title'] = item[1].name
            data['price'] = item[1].cost
            data['quantity'] = item[1].quantity
            data['description'] = item[1].description
            contents.append(data)
        return contents

    @property
    def currency(self):
        return u"$"

    @property
    def portal_url(self):
        url_tool = getToolByName(self.context, 'portal_url')
        return url_tool.getPortalObject().absolute_url()

    def _isSensibleContext(self):
        view = self.request.steps[-1].replace('@@', '')
        if view in self.contextsWherePortletShouldNotShow:
            return False
        return True

    render = ViewPageTemplateFile('cartlisting.pt')


class CartListingPortletAddForm(base.NullAddForm):

    def create(self):
        return CartListingPortletAssignment()
