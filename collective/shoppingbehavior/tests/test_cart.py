# -*- coding: utf-8 -*-

import unittest2 as unittest
import fudge
from collective.shoppingbehavior import shop
from collective.shoppingbehavior.behaviors import NamedPrice, PriceList


class MockCart(dict):

    def size(self):
        qty = 0
        for item in self.values():
            if hasattr(item, 'quantity'):
                qty += item.quantity

        return qty


class MockContext(object):

        def __init__(self, id, title):
            self.id = id
            self.title = title
            self.description = "A test description"


class TestShopper(unittest.TestCase):

    @fudge.test
    def testCanAddALineItem(self):
        fakeLineItem = (fudge.Fake('LineItem')
                             .has_attr(item_id="foo", quantity=0))

        fixture = shop.Shopper(MockCart())
        self.assertEqual('foo', fixture.add(fakeLineItem))
        self.failUnless(fixture.contains("foo"))

    @fudge.test
    def testCanAddAdditionalLineItems(self):
        fakeLineItem1 = (fudge.Fake('LineItem')
                              .has_attr(item_id="foo", quantity=2))
        fakeLineItem2 = (fudge.Fake('LineItem')
                              .has_attr(item_id="bar", quantity=1))
        fixture = shop.Shopper(MockCart())
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
        fixture = shop.Shopper(MockCart())
        fixture.add(fakeLineItem1)
        fixture.add(fakeLineItem2)
        self.assertEqual(1, fixture.size())

    @fudge.test
    def testSizeDelegatesToCartDependency(self):
        mock_cart = (fudge.Fake()
                          .provides('__setitem__')
                          .expects('size'))
        fixture = shop.Shopper(mock_cart)
        fixture.size()


class TestNamingPolicy(unittest.TestCase):

    def testConstructsLineFullIdForNamedPriceAndContext(self):
        np = NamedPrice(2.99, u"price one")
        mock_context = MockContext(id=u"søme id", title=u"")
        naming = shop.StdNamingPolicy(np, mock_context)
        self.assertEqual(u"søme id-price one", naming.id())

    def testConstructsFullTitleForNamedPriceAndContext(self):
        np = NamedPrice(2.99, u"price one")
        mock_context = MockContext(id=u"some id", title=u"contéxt title")
        naming = shop.StdNamingPolicy(np, mock_context)
        self.assertEqual(u"contéxt title (price one)", naming.title())


class TestLineItemFactory(unittest.TestCase):

    def testSkipsLineItemIfQuantityIsZero(self):
        context = MockContext(id="some ID", title="some title")
        priceList = PriceList()
        priceList.append(NamedPrice(2.99, u"price one"))
        addRequest = [{"id": u'price one', "quantity": '0'}]
        factory = shop.LineItemFactory(priceList, context, addRequest)
        lineItems = factory.create()
        self.assertEqual(0, len(lineItems),
            "Should return an empty list if quantity is 0!")

    def testSkipsLineItemIfQuantityIsEmpty(self):
        context = MockContext(id="some ID", title="some title")
        priceList = PriceList()
        priceList.append(NamedPrice(2.99, u"price one"))
        addRequest = [{"id": u'price one', "quantity": ' '}]
        factory = shop.LineItemFactory(priceList, context, addRequest)
        lineItems = factory.create()
        self.assertEqual(0, len(lineItems),
            "Should return an empty list if quantity is empty!")

    @fudge.patch('collective.shoppingbehavior.shop.IUUID')
    def testCreatesSingleLineItem(self, IUUID):
        IUUID.expects_call()
        context = MockContext(id="some ID", title="some title")
        priceList = PriceList()
        priceList.append(NamedPrice(2.99, u"price one"))
        addRequest = [{"id": u'price one', "quantity": '2'}]
        factory = shop.LineItemFactory(priceList, context, addRequest)
        lineItems = factory.create()
        self.assertEqual(1, len(lineItems),
            "Should return a list with one LineItem!")
        self.assertEqual(2, lineItems[0].quantity)
        self.assertEqual("some ID-price one", lineItems[0].item_id)

    @fudge.patch('collective.shoppingbehavior.shop.IUUID')
    def testCreatesMultipleLineItems(self, IUUID):
        IUUID.expects_call()
        context = MockContext(id="some ID", title="some title")
        priceList = PriceList()
        priceList.extend([NamedPrice(2.99, u"price one"),
                          NamedPrice(3.99, u"price two")])
        addRequest = [{"id": u'price one', "quantity": '2'},
                      {"id": u'price two', "quantity": '3'}]
        factory = shop.LineItemFactory(priceList, context, addRequest)
        lineItems = factory.create()
        self.assertEqual(2, len(lineItems),
            "Should return a list with two LineItems!")
        self.assertEqual(2, lineItems[0].quantity)
        self.assertEqual("some ID-price one", lineItems[0].item_id)
        self.assertEqual(2.99, lineItems[0].cost)
        self.assertEqual(3, lineItems[1].quantity)
        self.assertEqual("some ID-price two", lineItems[1].item_id)
        self.assertEqual(3.99, lineItems[1].cost)
