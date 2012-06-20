from zope import interface as zif
from five import grok
from zope import schema
from plone.directives import form
from z3c.form.interfaces import IDataConverter, NO_VALUE
from z3c.form.converter import BaseDataConverter
from collective.z3cform.datagridfield import DataGridFieldFactory, IDataGridField

from collective.shoppingbehavior import _

EMPTY_PRICELIST = None


class IPotentiallyPriced(zif.Interface):
    """ Marker interface for content types that can have pricing enabled. This
        interface on type for which the IPriced behavior is enabled.
    """


class INamedPriceSchema(zif.Interface):
    name = schema.TextLine(title=u"Name", required=False)
    price = schema.Decimal(title=u"Price")


class NamedPrice(object):
    """ A price may have a name associated with it which distinguishes it
        amoung the other prices in the pricelist. For example "members" vs.
        "non-members".
    """
    zif.implements(INamedPriceSchema)

    def __init__(self, price, name=u''):
        self.price = price
        self.name = name


class PriceList(list):
    """ A list of available prices """
    def __repr__(self):
        return "PriceList%s" % list.__repr__(self)

    def by_name(self, name):
        """ Return a NamedPrice by name from this PriceList
        """
        matches = [np for np in self if np.name == name]
        if matches:
            return matches[0]
        return None


class PriceListField(schema.List):
    """ We need to have a unique class for the field list so that we
        can apply a custom adapter.
    """
    pass


class IPriced(form.Schema):
    """ Add a price list to a content object
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
        missing_value=EMPTY_PRICELIST,
    )

    @zif.invariant
    def priceMustBeSetIfEnabled(data):
        if data.enabled and data.pricelist == EMPTY_PRICELIST:
            raise zif.Invalid(
                _(u"At least one price must be set in order for pricing to be enabled."))

zif.alsoProvides(IPriced, form.IFormFieldProvider)


class GridDataConverter(grok.MultiAdapter, BaseDataConverter):
    """ Convert between the PriceList object and a data structure expected by
        the widget.
    """

    grok.adapts(PriceListField, IDataGridField)
    grok.implements(IDataConverter)

    def toWidgetValue(self, value):
        rv = list()
        if value is not EMPTY_PRICELIST:
            for row in value:
                d = dict()
                for name, field in schema.getFieldsInOrder(INamedPriceSchema):
                    d[name] = getattr(row, name)
                rv.append(d)

        return rv

    def toFieldValue(self, value):
        rv = PriceList()
        for row in value:
            d = dict()
            for name, field in schema.getFieldsInOrder(INamedPriceSchema):
                if row.get(name, NO_VALUE) != NO_VALUE:
                    d[name] = row.get(name)
            rv.append(NamedPrice(**d))
        return rv
