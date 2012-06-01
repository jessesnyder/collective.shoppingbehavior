from five import grok
from Acquisition import aq_inner
from zope.component import queryMultiAdapter
from plone.uuid.interfaces import IUUID
from plone.app.layout.navigation.interfaces import INavigationRoot
from Products.statusmessages.interfaces import IStatusMessage
from Products.CMFPlone.utils import safe_unicode
from getpaid.core.interfaces import IPayableLineItem
from getpaid.core.interfaces import ILineItemFactory
from getpaid.core.interfaces import IShoppingCart
from getpaid.core.item import PayableLineItem
from groundwire.checkout.utils import get_cart
from groundwire.checkout.utils import redirect_to_checkout

from collective.shoppingbehavior import behaviors


class ICallbackLineItem(IPayableLineItem):
    """ A line item with an after_charged() callback for use with
        groundwire.checkout
    """
    def after_charged():
        """ This method will be called by the groundwire.checkout payment
            transaction machinery if defined.
        """


class CallbackLineItem(PayableLineItem):
    def after_charged(self):
        pass


class CallbackLineItemFactory(grok.MultiAdapter):
    """ Responsible for generating a LineItem for a buyable object and adding
        it to the cart.
    """
    grok.provides(ILineItemFactory)
    grok.adapts(IShoppingCart, behaviors.IPotentiallyPriced)

    lineitemType = CallbackLineItem

    def __init__(self, cart, item):
        self.cart = cart
        self.item = item
        self.priced = behaviors.IPriced(self.item, None)

    def create(self):
        if self.priced is None:
            return None
        lineitem = self.lineitemType()
        self._initLineitem(lineitem)
        self._addToCart(lineitem)

        return lineitem

    def _addToCart(self, lineitem):
        if lineitem.item_id in self.cart:
            del self.cart[lineitem.item_id]
        self.cart[lineitem.item_id] = lineitem

    def _initLineitem(self, lineitem):
        lineitem.cost = self.priced.price
        lineitem.item_id = self.item.id
        lineitem.name = safe_unicode(self.item.title)
        lineitem.description = safe_unicode(self.item.description)
        lineitem.quantity = 0
        lineitem.uid = IUUID(self.item)


class Cart(object):
    """ Responsible for knowing about the details of carts, lineitems and
        checkout forms.
    """
    def __init__(self):
        self.cart = get_cart()

    def add(self, obj, qty):
        lineitem_factory = queryMultiAdapter((self.cart, obj), ILineItemFactory)
        if lineitem_factory is None:
            return False
        lineitem = lineitem_factory.create()
        lineitem.quantity = qty
        return lineitem.item_id

    def checkout(self):
        redirect_to_checkout()

    def contains(self, item_id):
        return item_id in self.cart

    def size(self):
        return self.cart.size()

    def items(self):
        return self.cart.items()

    def remove(self, item_id):
        if item_id in self.cart:
            del self.cart[item_id]

    def update_quantity(self, item_id, qty):
        if not self.contains(item_id):
            return
        if qty < 1:
            self.remove(item_id)
        else:
            lineitem = self.cart[item_id]
            lineitem.quantity = qty


class CheckoutView(grok.View):
    """ Redirects the user to the checkout page.
    """
    grok.name('csb-checkout')
    grok.context(INavigationRoot)
    grok.require('zope2.View')

    def update(self):
        cart = Cart()
        cart.checkout()

    def render(self):
        return u''


class CartView(grok.View):
    """ Adds the context object to the shopping cart if possible.
    """
    grok.name('xsb-cart-add')
    grok.context(behaviors.IPotentiallyPriced)
    grok.require('zope2.View')

    def update(self):
        cart = Cart()
        context = aq_inner(self.context)
        qty = int(self.request.form.get('quantity', 0))
        added = cart.add(context, qty)
        if added:
            IStatusMessage(self.request).addStatusMessage(
                            u"Shopping cart updated.", type='info')
            self.request.response.redirect(self.context.absolute_url())

    def render(self):
        return u''


class CartUpdate(grok.View):
    """ Update quantities or remove items from the shopping cart """
    grok.name("csb-cart-update")
    grok.context(INavigationRoot)
    grok.require('zope2.View')

    def update(self):
        self.cart = Cart()
        self.has_items = self.cart.size() > 0
        self.contents = self.items()
        if "update_cart" in self.request.form:
            self.update_cart(self.request.form)
            IStatusMessage(self.request).addStatusMessage(
                u"Shopping cart updated.", type='info')
            self.request.response.redirect(
                self.context.absolute_url() + '/' + self.__name__)

        return ''

    def update_cart(self, form):
        new_qtys = form.get('quantities', [])
        for qty_info in new_qtys:
            item_id = qty_info['id']
            qty = int(qty_info['quantity'])
            self.cart.update_quantity(item_id, qty)

    def items(self):
        contents = []
        cart_contents = self.cart.items()
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
