from plone.app.testing import PloneSandboxLayer
from plone.app.testing import applyProfile
from plone.app.testing import PLONE_FIXTURE
from plone.app.testing import IntegrationTesting

from zope.configuration import xmlconfig


class ExpShopping(PloneSandboxLayer):

    defaultBases = (PLONE_FIXTURE,)

    def setUpZope(self, app, configurationContext):
        # Load ZCML
        import experimental.shoppingbehavior
        xmlconfig.file('configure.zcml', experimental.shoppingbehavior,
                            context=configurationContext)

    def setUpPloneSite(self, portal):
        applyProfile(portal, 'experimental.shoppingbehavior:default')

EXP_SHOPPING_FIXTURE = ExpShopping()
EXP_SHOPPING_INTEGRATION_TESTING = IntegrationTesting(
        bases=(EXP_SHOPPING_FIXTURE,), name="ExpShopping:Integration")
