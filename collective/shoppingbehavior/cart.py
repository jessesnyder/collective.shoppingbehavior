from five import grok
from Acquisition import aq_inner
from plone.uuid.interfaces import IUUID
from plone.app.layout.navigation.interfaces import INavigationRoot
from Products.statusmessages.interfaces import IStatusMessage
from Products.CMFPlone.utils import safe_unicode
from getpaid.core.interfaces import IPayableLineItem
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


class Shopper(object):
    """ Wrapper around a shopping cart, which should provide
        getpaid.core.interfaces.IShoppingCart.
    """
    def __init__(self, cart):
        self.cart = cart

    def add(self, lineitem):
        if lineitem.item_id in self.cart:
            del self.cart[lineitem.item_id]
        self.cart[lineitem.item_id] = lineitem
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
        cart = Shopper(get_cart())
        cart.checkout()

    def render(self):
        return u''


class CartAddingView(grok.View):
    """ Adds creates LineItems based on the context and the requests and
        adds them to the shopping cart via a Shopper.
    """
    grok.name('csb-cart-add')
    grok.context(behaviors.IPotentiallyPriced)
    grok.require('zope2.View')

    def update(self):
        shopper = Shopper(get_cart())
        to_add = self._lineitems(self.request.form.get('addables', []))
        successes = []
        for addition in to_add:
            successes.append(shopper.add(addition))
        if successes:
            IStatusMessage(self.request).addStatusMessage(
                            u"%s item[s] added to your cart." % len(successes),
                            type='info')
            self.request.response.redirect(self.context.absolute_url())

    def render(self):
        return u''

    def _lineitems(self, to_add):
        """ [{'id': 'members', 'quantity': '1'},
             {'id': 'non-members', 'quantity': ''}]
        """
        context = aq_inner(self.context)
        lineitems = []
        for item in to_add:
            if not item['quantity']:
                continue
            priced = behaviors.IPriced(context)
            lineitem = CallbackLineItem()
            namedprice = priced.pricelist.by_name(item['id'])
            if not namedprice:
                continue
            lineitem.cost = namedprice.price
            lineitem.item_id = namedprice.id_in_context(context)
            lineitem.name = namedprice.title_in_context(context)
            lineitem.description = safe_unicode(context.description)
            lineitem.quantity = int(item['quantity'])
            lineitem.uid = IUUID(context)
            lineitems.append(lineitem)
        return lineitems


class CartUpdate(grok.View):
    """ Update quantities or remove items from the shopping cart """
    grok.name("csb-cart-update")
    grok.context(INavigationRoot)
    grok.require('zope2.View')

    def update(self):
        self.cart = Shopper(get_cart())
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

    @property
    def currency(self):
        return u"$"
