from plone.app.testing import PloneSandboxLayer
from plone.app.testing import applyProfile
from plone.app.testing import PLONE_FIXTURE
from plone.app.testing import IntegrationTesting
from zope.interface import implements
from zope.annotation.interfaces import IAttributeAnnotatable

from zope.configuration import xmlconfig


class StubContext(object):
    implements(IAttributeAnnotatable)


class ExpShopping(PloneSandboxLayer):

    defaultBases = (PLONE_FIXTURE,)

    def setUpZope(self, app, configurationContext):
        # Load ZCML
        import collective.shoppingbehavior
        xmlconfig.file('configure.zcml', collective.shoppingbehavior,
                            context=configurationContext)

    def setUpPloneSite(self, portal):
        applyProfile(portal, 'collective.shoppingbehavior:default')

EXP_SHOPPING_FIXTURE = ExpShopping()
EXP_SHOPPING_INTEGRATION_TESTING = IntegrationTesting(
        bases=(EXP_SHOPPING_FIXTURE,), name="ExpShopping:Integration")
