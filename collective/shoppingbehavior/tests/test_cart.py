import unittest2 as unittest
import fudge
from zope.publisher.browser import TestRequest
from collective.shoppingbehavior import cart


class MockCart(dict):

    def size(self):
        qty = 0
        for item in self.values():
            if hasattr(item, 'quantity'):
                qty += item.quantity

        return qty


class TestShopper(unittest.TestCase):

    @fudge.test
    def testCanAddALineItem(self):
        fakeLineItem = (fudge.Fake('LineItem')
                             .has_attr(item_id="foo", quantity=0))

        fixture = cart.Shopper(MockCart())
        self.assertEqual('foo', fixture.add(fakeLineItem))
        self.failUnless(fixture.contains("foo"))

    @fudge.test
    def testCanAddAdditionalLineItems(self):
        fakeLineItem1 = (fudge.Fake('LineItem')
                              .has_attr(item_id="foo", quantity=2))
        fakeLineItem2 = (fudge.Fake('LineItem')
                              .has_attr(item_id="bar", quantity=1))
        fixture = cart.Shopper(MockCart())
        fixture.add(fakeLineItem1)
        fixture.add(fakeLineItem2)
        self.failUnless(fixture.contains("foo"))
        self.failUnless(fixture.contains("bar"))
        self.assertEqual(3, fixture.size())

    @fudge.test
    def testAddingLineItemWithSameIdReplacesRatherThanAdds(self):
        fakeLineItem1 = (fudge.Fake('LineItem')
                              .has_attr(item_id="foo", quantity=2))
        fakeLineItem2 = (fudge.Fake('LineItem')
                              .has_attr(item_id="foo", quantity=1))
        fixture = cart.Shopper(MockCart())
        fixture.add(fakeLineItem1)
        fixture.add(fakeLineItem2)
        self.assertEqual(1, fixture.size())

    @fudge.test
    def testSizeDelegatesToCartDependency(self):
        mock_cart = (fudge.Fake()
                          .provides('__setitem__')
                          .expects('size'))
        fixture = cart.Shopper(mock_cart)
        fixture.size()


class TestLineItemFactory(unittest.TestCase):

    def testSkipsLineItemIFQuantityIsZero(self):
        self.fail()

    def testCreatesSingleLineItem(self):
        self.fail()

    def testCreatesMultipleLineItems(self):
        self.fail()


class TestCartView(unittest.TestCase):
    """ The CartAddingView instantiates a Cart object and the calls its add() method
        with the context object and the quantity pulled from the request. These
        tests mock out the Cart class in order to test these interactions in
        isolation.
    """

    @fudge.patch('collective.shoppingbehavior.cart.Cart')
    def testCartAddingViewCallsWithZeroQtyByDefault(self, Cart):
        context = object()
        fakeCartInstance = (fudge.Fake()
                                 .provides('add')
                                 .with_args(context, 0)
                                 .returns('some id'))
        fakeCartInstance.expects('checkout')
        Cart.expects_call().returns(fakeCartInstance)
        view = cart.CartAddingView(context, TestRequest())
        view.update()

    @fudge.patch('collective.shoppingbehavior.cart.Cart')
    def testCartAddingViewCallsWithQtyFromRequest(self, Cart):
        context = object()
        testQty = '3'
        request = TestRequest(form=dict(quantity=testQty))
        fakeCartInstance = (fudge.Fake()
                                 .provides('add')
                                 .with_args(context, int(testQty))
                                 .returns('some id'))
        fakeCartInstance.expects('checkout')
        Cart.expects_call().returns(fakeCartInstance)
        view = cart.CartAddingView(context, request)
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
        view = cart.CartAddingView(context, request)
        view.update()
