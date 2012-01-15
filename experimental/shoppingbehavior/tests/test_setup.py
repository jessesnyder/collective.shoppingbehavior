import unittest2 as unittest
from zope.component import queryUtility
from plone.behavior.interfaces import IBehavior

from experimental.shoppingbehavior.testing import EXP_SHOPPING_INTEGRATION_TESTING


class TestConfiguration(unittest.TestCase):

    layer = EXP_SHOPPING_INTEGRATION_TESTING

    def testBehaviorInRegistry(self):
        priced = queryUtility(IBehavior,
                name='experimental.shoppingbehavior.behaviors.IPriced')
        self.failUnless(priced is not None)

    def testBehaviorProvidesFields(self):
        from plone.directives.form import IFormFieldProvider
        priced = queryUtility(IBehavior,
                name='experimental.shoppingbehavior.behaviors.IPriced')
        self.assertTrue(IFormFieldProvider.providedBy(priced.interface))
