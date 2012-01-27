from zope.interface import alsoProvides

from zope import schema

from plone.directives import form


class IPriced(form.Schema):
    """ Add a price to a content object
    """

    form.fieldset(
            'pricing',
            label=u'Pricing',
            fields=('enabled', 'price',),
        )
    enabled = schema.Bool(
        title=u'Enabled',
        description=u'Enable pricing for this item',
        default=False,
        required=False,
    )
    price = schema.Decimal(
        title=u'Price',
        description=u'The price for this item',
        required=False,
    )

alsoProvides(IPriced, form.IFormFieldProvider)
