from zope.interface import alsoProvides

from zope import schema

from plone.directives import form


class IPriced(form.Schema):
    """ Add a price to a content object
    """

    form.fieldset(
            'pricing',
            label=u'Pricing',
            fields=('price',),
        )
    price = schema.Float(
        title=u'Price',
        description=u'The price for this item',
        required=False,
    )

alsoProvides(IPriced, form.IFormFieldProvider)
