import unittest2 as unittest
import fudge
from zope.publisher.browser import TestRequest
from collective.shoppingbehavior import cart


class TestCart(unittest.TestCase):

    @fudge.patch('collective.shoppingbehavior.cart.get_cart')
    @fudge.patch('collective.shoppingbehavior.cart.queryMultiAdapter')
    def testAdd(self, fake_get_cart, queryMultiAdapter):
        # set up a fake cart
        (fake_get_cart.expects_call()
                      .returns_fake()
                      .provides('__setitem__'))
        fixture = cart.Cart()
        # set up a fake queryMultiAdapter chain of madness
        fakeLineItem = (fudge.Fake('LineItem')
                             .has_attr(item_id="foo", quantity=0))
        fakeLineItemFactory = (fudge.Fake('LineItemFactory')
                                    .provides('create')
                                    .returns(fakeLineItem))
        (queryMultiAdapter.expects_call()
                          .with_arg_count(2)
                          .returns(fakeLineItemFactory))

        self.assertEqual('foo', fixture.add(None, 3))
        self.assertEqual(3, fakeLineItem.quantity)


class TestCartView(unittest.TestCase):
    """ The CartView instantiates a Cart object and the calls its add() method
        with the context object and the quantity pulled from the request. These
        tests mock out the Cart class in order to test these interactions in
        isolation.
    """

    @fudge.patch('collective.shoppingbehavior.cart.Cart')
    def testCartViewCallsWithZeroQtyByDefault(self, Cart):
        context = object()
        fakeCartInstance = (fudge.Fake()
                                 .provides('add')
                                 .with_args(context, 0)
                                 .returns('some id'))
        fakeCartInstance.expects('checkout')
        Cart.expects_call().returns(fakeCartInstance)
        view = cart.CartView(context, TestRequest())
        view.update()

    @fudge.patch('collective.shoppingbehavior.cart.Cart')
    def testCartViewCallsWithQtyFromRequest(self, Cart):
        context = object()
        testQty = '3'
        request = TestRequest(form=dict(quantity=testQty))
        fakeCartInstance = (fudge.Fake()
                                 .provides('add')
                                 .with_args(context, int(testQty))
                                 .returns('some id'))
        fakeCartInstance.expects('checkout')
        Cart.expects_call().returns(fakeCartInstance)
        view = cart.CartView(context, request)
        view.update()

    @fudge.patch('collective.shoppingbehavior.cart.Cart')
    def testOnlyCallsCheckoutIfAddSucceeds(self, Cart):
        context = object()
        testQty = '3'
        request = TestRequest(form=dict(quantity=testQty))
        fakeCartInstance = (fudge.Fake()
                                 .provides('add')
                                 .with_args(context, int(testQty))
                                 .returns(False))
        Cart.expects_call().returns(fakeCartInstance)
        view = cart.CartView(context, request)
        view.update()
