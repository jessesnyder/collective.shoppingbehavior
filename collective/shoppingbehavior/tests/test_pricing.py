import unittest2 as unittest
from StringIO import StringIO
from decimal import Decimal

from zope.configuration import xmlconfig
from zope import component
from zope import interface as zif
from plone.behavior.interfaces import IBehaviorAssignable
from plone.behavior.interfaces import IBehavior

from collective.shoppingbehavior import behaviors
from collective.shoppingbehavior.testing import StubContext

from plone.testing.zca import UNIT_TESTING


configuration = """\
<configure
    package="collective.shoppingbehavior"
    xmlns="http://namespaces.zope.org/zope"
    xmlns:plone="http://namespaces.plone.org/plone"
    i18n_domain="collective.shoppingbehavior">

  <include package="zope.component" file="meta.zcml" />
  <include package="plone.behavior" file="meta.zcml" />
  <include package="zope.annotation" />

  <plone:behavior
      title="Pricing"
      description="Store a price for the adapted item and boolean 'active setting'"
      provides=".behaviors.IPriced"
      marker=".behaviors.IPotentiallyPriced"
      factory="plone.behavior.AnnotationStorage" />

</configure>
"""


class TestingAssignable(object):
    zif.implements(IBehaviorAssignable)
    component.adapts(zif.Interface)
    enabled = [behaviors.IPriced]

    def __init__(self, context):
        self.context = context

    def supports(self, behavior_interface):
        return behavior_interface in self.enabled

    def enumerateBehaviors(self):
        for e in self.enabled:
            yield component.queryUtility(IBehavior, name=e.__identifier__)


class TestPricing(unittest.TestCase):

    layer = UNIT_TESTING

    def setUp(self):
        xmlconfig.xmlconfig(StringIO(configuration))
        component.provideAdapter(TestingAssignable)
        self.context = StubContext()

    def testAdaptation(self):
        priced = behaviors.IPriced(self.context)
        self.assertTrue(priced is not None)

    def testEnabled(self):
        priced = behaviors.IPriced(self.context)
        self.assertTrue(hasattr(priced, 'enabled'))
        # should be false by default
        self.failIf(priced.enabled)
        # should be settable
        priced.enabled = True
        self.assertEqual(True, behaviors.IPriced(self.context).enabled)

    def testPricelist(self):
        priced = behaviors.IPriced(self.context)
        self.assertTrue(hasattr(priced, 'pricelist'))
        self.assertEqual("PriceList", priced.pricelist.__class__.__name__)

    def testPriceListEmtpyByDefault(self):
        priced = behaviors.IPriced(self.context)
        import pdb; pdb.set_trace()
        self.assertEqual(behaviors.PriceList(), priced.pricelist)

    def testPriceListAcceptsNewNamedPriceObjects(self):
        priced = behaviors.IPriced(self.context)
        priced.pricelist.append(behaviors.NamedPrice(2.99))
        self.assertEqual(2.99, behaviors.IPriced(self.context).pricelist[0].price)

    # def testInvariants(self):
    #     validation = behaviors.IPriced.validateInvariants
    #     context = StubContext()
    #     priced = behaviors.IPriced(context)
    #     priced.enabled = True
    #     self.assertRaises(zif.Invalid, validation, priced)
    #     # set a price and we're OK
    #     priced.price = 2.99
    #     self.assertEqual(None, validation(priced))
