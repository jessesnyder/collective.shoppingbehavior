from five import grok
from Acquisition import aq_inner
from zope.component import queryMultiAdapter
from plone.uuid.interfaces import IUUID
from Products.CMFPlone.utils import safe_unicode
from getpaid.core.interfaces import IPayableLineItem
from getpaid.core.interfaces import ILineItemFactory
from getpaid.core.interfaces import IShoppingCart
from getpaid.core.item import PayableLineItem
from groundwire.checkout.utils import get_cart
from groundwire.checkout.utils import redirect_to_checkout

from experimental.shoppingbehavior import behaviors


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
    grok.adapts(IShoppingCart, behaviors.IPriced)

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


class CartView(grok.View):
    """ Adds the context object to the shopping cart if possible.
    """
    grok.name('xsb-cart-add')
    grok.context(behaviors.IPriced)
    grok.require('zope2.View')

    def update(self):
        cart = Cart()
        context = aq_inner(self.context)
        qty = int(self.request.form.get('quantity', 0))
        added = cart.add(context, qty)
        if added:
            cart.checkout()

    def render(self):
        return u''
