import unittest2 as unittest
from StringIO import StringIO

from zope.configuration import xmlconfig
from zope.component import adapts
from zope.component import queryUtility
from zope.component import provideAdapter
from zope.interface import Interface
from zope.interface import implements
from zope.interface import alsoProvides
from zope.annotation.interfaces import IAttributeAnnotatable
from plone.behavior.interfaces import IBehaviorAssignable
from plone.behavior.interfaces import IBehavior

from experimental.shoppingbehavior import behaviors

from plone.testing.zca import UNIT_TESTING


class SomeInterface(Interface):
    pass


class SomeContext(object):
    implements(IAttributeAnnotatable)


configuration = """\
<configure
    package="experimental.shoppingbehavior"
    xmlns="http://namespaces.zope.org/zope"
    xmlns:plone="http://namespaces.plone.org/plone"
    i18n_domain="experimental.shoppingbehavior">

  <include package="zope.component" file="meta.zcml" />
  <include package="plone.behavior" file="meta.zcml" />
  <include package="zope.annotation" />

  <plone:behavior
      title="Pricing"
      description="Store a price for the adapted item and boolean 'active setting'"
      provides=".behaviors.IPriced"
      factory="plone.behavior.AnnotationStorage" />

</configure>
"""


class TestingAssignable(object):
    implements(IBehaviorAssignable)
    adapts(Interface)
    enabled = [behaviors.IPriced]

    def __init__(self, context):
        self.context = context

    def supports(self, behavior_interface):
        return behavior_interface in self.enabled

    def enumerateBehaviors(self):
        for e in self.enabled:
            yield queryUtility(IBehavior, name=e.__identifier__)


class TestPricing(unittest.TestCase):

    layer = UNIT_TESTING

    def setUp(self):
        xmlconfig.xmlconfig(StringIO(configuration))
        provideAdapter(TestingAssignable)

    def testAdaptedContentHasPriceAndActive(self):
        context = SomeContext()
        priced = behaviors.IPriced(context)
        self.assertTrue(priced is not None)
        # starts with null price by default
        self.assertEqual(None, priced.price)
        # but you can assign and re-obtain the attributes
        priced.price = 2.99
        self.assertEqual(2.99, behaviors.IPriced(context).price)


class TestPricingConfig(unittest.TestCase):
    """ Test enabling and disabling pricing behavior """

    layer = UNIT_TESTING

    configuration = """\
<configure
    package="experimental.shoppingbehavior"
    xmlns="http://namespaces.zope.org/zope"
    xmlns:plone="http://namespaces.plone.org/plone"
    i18n_domain="experimental.shoppingbehavior">

  <include package="zope.component" file="meta.zcml" />
  <include package="zope.annotation" />

</configure>
"""

    def setUp(self):
        xmlconfig.xmlconfig(StringIO(self.configuration))
        provideAdapter(behaviors.PricingStatus)

    def testAdapterLookupFailsWithoutSupportInterface(self):
        context = SomeContext()
        self.assertRaises(TypeError, behaviors.IPricingStatus, context)

    def testAdapterLookupWithSupportInterface(self):
        context = SomeContext()
        alsoProvides(context, behaviors.IPotentiallyPriced)
        config = behaviors.IPricingStatus(context)
        self.assertTrue(config is not None)

    def testIsPriceEnableable(self):
        context = SomeContext()
        alsoProvides(context, behaviors.IPotentiallyPriced)
        config = behaviors.IPricingStatus(context)
        self.assertTrue(config.isPriceEnableable())

    def testEnableAndDisable(self):
        context = SomeContext()
        alsoProvides(context, behaviors.IPotentiallyPriced)
        config = behaviors.IPricingStatus(context)
        config.enablePricing()
        self.failUnless(config.isPriceEnabled())
        self.failIf(config.isPriceEnableable())
        config.disablePricing()
        self.failIf(config.isPriceEnabled())
        self.failUnless(config.isPriceEnableable())
