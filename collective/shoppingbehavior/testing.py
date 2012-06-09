from plone.app.testing import PloneSandboxLayer
from plone.app.testing import applyProfile
from plone.app.testing import PLONE_FIXTURE
from plone.app.testing import IntegrationTesting

from zope.configuration import xmlconfig


class CollectiveShopping(PloneSandboxLayer):

    defaultBases = (PLONE_FIXTURE,)

    def setUpZope(self, app, configurationContext):
        # Load ZCML
        import collective.shoppingbehavior
        xmlconfig.file('configure.zcml', collective.shoppingbehavior,
                            context=configurationContext)

    def setUpPloneSite(self, portal):
        applyProfile(portal, 'collective.shoppingbehavior:default')

COLLECTIVE_SHOPPING_FIXTURE = CollectiveShopping()
COLLECTIVE_SHOPPING_INTEGRATION_TESTING = IntegrationTesting(
        bases=(COLLECTIVE_SHOPPING_FIXTURE,),
        name="CollectiveShopping:Integration")
