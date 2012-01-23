import unittest2 as unittest
from plone.testing.zca import UNIT_TESTING
from zope.interface import implements
from zope.component import adapts
from mock import Mock, patch
from getpaid.core.interfaces import ILineItemFactory
from getpaid.core.interfaces import IShoppingCart

from experimental.shoppingbehavior.behaviors import IPotentiallyPriced
from experimental.shoppingbehavior import cart


class TestCartManualMocks(unittest.TestCase):

    def setUp(self):
        self.fixture = cart.Cart()
        self.mockGetpaidCart = {}
        cart.get_cart = Mock(return_value=self.mockGetpaidCart)

    def testAddWithSuccessfulAdapterLookup(self):
        factory = Mock()
        lineitem = Mock()
        lineitem.quantity = 0
        factory.create = Mock(return_value=lineitem)
        cart.queryMultiAdapter = Mock(return_value=factory)
        item = Mock()
        qty = 2
        self.assertTrue(self.fixture.add(item, qty))
        cart.queryMultiAdapter.assert_called_with(
            (self.mockGetpaidCart, item), ILineItemFactory)
        self.assertEqual(qty, lineitem.quantity)

    def testWhenAdapterLookupFails(self):
        cart.queryMultiAdapter = Mock(return_value=None)
        item = Mock()
        qty = 2
        self.assertFalse(self.fixture.add(item, qty))


class TestCartWithPatch(unittest.TestCase):

    def setUp(self):
        self.fixture = cart.Cart()

    @patch('experimental.shoppingbehavior.cart.queryMultiAdapter')
    @patch('experimental.shoppingbehavior.cart.get_cart')
    def testAddCallsGetCart(self, queryMultiAdapter, get_cart):
        self.fixture.add(Mock(), 2)
        queryMultiAdapter.assert_called_once
        get_cart.assert_called_once

from zope.interface import alsoProvides



from zope.component import provideAdapter


class DummyLineFactory(object):
    implements(ILineItemFactory)
    adapts(IShoppingCart, IPotentiallyPriced)

    def __init__(self, cart, item):
        self.cart = cart
        self.item = item

    def create(self):
        self.cart[self.item.id] = self.item
        return self.item


mock_get_cart = Mock(return_value={})


class TestCartZCAInTact(unittest.TestCase):

    layer = UNIT_TESTING

    def setUp(self):
        self.fixture = cart.Cart()
        self.item = Mock()
        alsoProvides(self.item, IPotentiallyPriced)
        self.item.id = '123'
        provideAdapter(DummyLineFactory)

    @patch('experimental.shoppingbehavior.cart.get_cart', mock_get_cart)
    def testAdding(self):
        self.fixture.add(self.item, 2)
        mock_get_cart.assert_called_once


