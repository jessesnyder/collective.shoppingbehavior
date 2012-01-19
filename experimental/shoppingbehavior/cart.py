from five import grok
from Acquisition import aq_inner
from plone.uuid.interfaces import IUUID
from getpaid.core.interfaces import IPayableLineItem
from groundwire.checkout.utils import get_cart
from groundwire.checkout.utils import redirect_to_checkout

from experimental.shoppingbehavior import behaviors


class DefaultLineItemAdapter(grok.Adapter):
    """ The IPayableLineItem adapter lookup is used both by the portlet
        for adding items to the cart, and during payment processing
    """
    grok.context(behaviors.IPotentiallyPriced)
    grok.provides(IPayableLineItem)

    def __init__(self, context):
        self.context = context
        # This lookup will fail if the context doesn't actually have the
        # behavior enabled.
        self.cost = behaviors.IPriced(self.context).price
        self.item_id = self.context.id
        self.name = self.context.title
        self.description = self.context.description
        self.quantity = 0
        self.uid = IUUID(self.context)

    def after_charged(self):
        pass


class Cart(object):
    """ Responsible for adding items to the shopping cart and knowing where
        the checkout form lives
    """

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
            cart.checkout()

    def render(self):
        return u''
