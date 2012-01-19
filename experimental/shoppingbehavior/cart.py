from five import grok
from Acquisition import aq_inner
from plone.uuid.interfaces import IUUID
from getpaid.core.interfaces import IPayableLineItem
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


@grok.implementer(ICallbackLineItem)
@grok.adapter(behaviors.IPotentiallyPriced)
def defaultLineItemAdapter(context):
    """ The IPayableLineItem adapter lookup is used both by the portlet
        for adding items to the cart, and during payment processing
    """
    item = CallbackLineItem()
    item.cost = behaviors.IPriced(context).price
    item.item_id = context.id
    item.name = context.title
    item.description = context.description
    item.quantity = 0
    item.uid = IUUID(context)

    return item


class Cart(object):
    """ Responsible for adding items to the shopping cart and knowing where
        the checkout form lives
    """

    def add(self, obj, qty):
        lineitem = ICallbackLineItem(obj, None)
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
