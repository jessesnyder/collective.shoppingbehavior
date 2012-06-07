from zope import interface as zif
from five import grok
from zope import schema
from plone.directives import form
from collective.z3cform.datagridfield import DataGridFieldFactory, DictRow, IDataGridField
from z3c.form.interfaces import DISPLAY_MODE, HIDDEN_MODE, IDataConverter, NO_VALUE
from zope.schema import getFieldsInOrder
from z3c.form.converter import BaseDataConverter

from collective.shoppingbehavior import _


class IPotentiallyPriced(zif.Interface):
    """ Marker interface for content types that can have pricing enabled. This
        interface on type for which the IPriced behavior is enabled.
    """


class INamedPriceSchema(zif.Interface):
    name = schema.TextLine(title=u"Name", required=False)
    price = schema.Decimal(title=u"Price")


class NamedPrice(object):
    zif.implements(INamedPriceSchema)

    def __init__(self, price, name=u''):
        self.price = price
        self.name = name


class PriceList(list):
    pass


class PriceListField(schema.List):
    """We need to have a unique class for the field list so that we
       can apply a custom adapter.
    """
    pass


class IPriced(form.Schema):
    """ Add a price to a content object
    """

    form.fieldset(
            'pricing',
            label=u'Pricing',
            fields=('enabled', 'price', 'pricelist'),
        )
    enabled = schema.Bool(
        title=u'Enabled',
        description=u'Enable pricing for this item',
        default=False,
        required=False,
    )
    form.widget(pricelist=DataGridFieldFactory)
    pricelist = PriceListField(
        title=u"Price list",
        value_type=schema.Object(title=u"Price", schema=INamedPriceSchema),
        missing_value=None,
    )

    @zif.invariant
    def priceMustBeSetIfEnabled(data):
        if data.enabled and data.pricelist == None:
            raise zif.Invalid(
                _(u"At least one price must be set in order for pricing to be enabled."))

zif.alsoProvides(IPriced, form.IFormFieldProvider)


class GridDataConverter(grok.MultiAdapter, BaseDataConverter):
    """ Convert between the PriceList object and the widget. """

    grok.adapts(PriceListField, IDataGridField)
    grok.implements(IDataConverter)

    def toWidgetValue(self, value):
        """Simply pass the data through with no change"""
        rv = list()
        for row in value:
            d = dict()
            for name, field in getFieldsInOrder(INamedPriceSchema):
                d[name] = getattr(row, name)
            rv.append(d)

        return rv

    def toFieldValue(self, value):
        rv = PriceList()
        for row in value:
            d = dict()
            for name, field in getFieldsInOrder(INamedPriceSchema):
                if row.get(name, NO_VALUE) != NO_VALUE:
                    d[name] = row.get(name)
            rv.append(NamedPrice(**d))
        return rv
