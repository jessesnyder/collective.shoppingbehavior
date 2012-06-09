import unittest2 as unittest
from zope.interface import implements
from zope.component import queryUtility
from plone.behavior.interfaces import IBehavior
from zope.annotation.interfaces import IAttributeAnnotatable

from collective.shoppingbehavior.testing import COLLECTIVE_SHOPPING_INTEGRATION_TESTING


class SomeContext(object):
    implements(IAttributeAnnotatable)


class TestConfiguration(unittest.TestCase):

    layer = COLLECTIVE_SHOPPING_INTEGRATION_TESTING

    def testBehaviorInRegistry(self):
        priced = queryUtility(IBehavior,
                name='collective.shoppingbehavior.behaviors.IPriced')
        self.failUnless(priced is not None)

    def testBehaviorProvidesFields(self):
        from plone.directives.form import IFormFieldProvider
        priced = queryUtility(IBehavior,
                name='collective.shoppingbehavior.behaviors.IPriced')
        self.assertTrue(IFormFieldProvider.providedBy(priced.interface))
