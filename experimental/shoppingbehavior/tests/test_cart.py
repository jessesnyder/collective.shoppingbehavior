import unittest2 as unittest
import fudge
from experimental.shoppingbehavior import cart


class TestCartUnit(unittest.TestCase):

    @fudge.patch('experimental.shoppingbehavior.cart.get_cart')
    @fudge.patch('experimental.shoppingbehavior.cart.queryMultiAdapter')
    def testAdd(self, fake_get_cart, fake_queryMultiAdapter):
        # set up a fake cart
        (fake_get_cart.expects_call().returns_fake().provides('__setitem__'))
        fixture = cart.Cart()
        # set up a fake queryMultiAdapter chain of madness
        fakeLineItem = fudge.Fake('LineItem').has_attr(
                                            item_id="foo", quantity=0)
        fakeLineItemFactory = fudge.Fake('LineItemFactory').provides(
                                            'create').returns(fakeLineItem)
        (fake_queryMultiAdapter.expects_call().with_arg_count(2).
                returns(fakeLineItemFactory))

        self.assertEqual('foo', fixture.add(None, 3))
        self.assertEqual(3, fakeLineItem.quantity)
