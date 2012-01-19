from five import grok
from Acquisition import aq_inner
from getpaid.core.interfaces import IPayableLineItem
from groundwire.checkout.utils import get_cart
from groundwire.checkout.utils import redirect_to_checkout

from experimental.shoppingbehavior import behaviors


class DefaultLineItemAdapter(grok.Adapter):
    grok.context(behaviors.IPotentiallyPriced)
    grok.provides(IPayableLineItem)

    def __init__(self, buyable):
        self.cost = behaviors.IPriced(buyable).price
        self.item_id = buyable.id
        self.name = buyable.title
        self.description = buyable.description
        self.quantity = 0


class Cart(object):
    """ Responsible for adding items to the shopping cart """

    def add(self, obj, qty):
        lineitem = IPayableLineItem(obj, None)
        if lineitem is None:
            return False
        lineitem.quantity = qty
        cart = get_cart()
        if lineitem.item_id in cart:
            del cart[lineitem.item_id]
        cart[lineitem.item_id] = lineitem
        return True

    def checkout(self):
        redirect_to_checkout()


class CartView(grok.View):
    """ Add the context object to the shopping cart if possible.
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
            cart.checkout()

    def render(self):
        return u''
