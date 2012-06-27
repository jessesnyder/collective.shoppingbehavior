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


def getShopper():
    # Convenience method which builds a Shopper with a Cart
    return Shopper(get_cart())


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


class StdNamingPolicy(object):

    def __init__(self, namedprice, context):
        self.namedprice = namedprice
        self.context = context

    def title(self):
        return u"%s (%s)" % (safe_unicode(self.context.title),
                             safe_unicode(self.namedprice.name))

    def id(self):
        return u"%s-%s" % (safe_unicode(self.context.id),
                           safe_unicode(self.namedprice.name))


class LineItemFactory(object):

    def __init__(self, pricelist, context, addRequest, namingPolicy=StdNamingPolicy):
        self.pricelist = pricelist
        self.context = context
        self.addRequest = addRequest
        self.namingPolicy = namingPolicy

    def create(self):
        lineItems = []
        for item in self.addRequest:
            if not self._hasQuantity(item):
                continue
            namedprice = self.pricelist.by_name(item['id'])
            if not namedprice:
                continue
            lineitem = CallbackLineItem()
            naming = self.namingPolicy(namedprice, self.context)
            lineitem.quantity = int(item['quantity'])
            lineitem.cost = float(namedprice.price)
            lineitem.item_id = naming.id()
            lineitem.name = naming.title()
            lineitem.description = safe_unicode(self.context.description)
            lineitem.uid = IUUID(self.context)
            lineItems.append(lineitem)
        return lineItems

    def _hasQuantity(self, item):
        qty = item['quantity'].strip()
        if not qty:
            return False
        return bool(int(qty))


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
        shopper = getShopper()
        shopper.checkout()

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
        shopper = getShopper()
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
        """ to_add looks like this:

            [{'id': 'members', 'quantity': '1'},
             {'id': 'non-members', 'quantity': ''}]
        """
        context = aq_inner(self.context)
        priced = behaviors.IPriced(context)
        lineItemBuilder = LineItemFactory(priced.pricelist, context, to_add)
        return lineItemBuilder.create()


class CartUpdate(grok.View):
    """ Update quantities or remove items from the shopping cart """
    grok.name("csb-cart-update")
    grok.context(INavigationRoot)
    grok.require('zope2.View')

    def update(self):
        self.shopper = getShopper()
        self.has_items = self.shopper.size() > 0
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
            self.shopper.update_quantity(item_id, qty)

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
