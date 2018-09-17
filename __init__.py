# This file is part product_rivals_minderest module for Tryton.
# The COPYRIGHT file at the top level of this repository contains
# the full copyright notices and license terms.
from trytond.pool import Pool
from . import rivals
from . import product


def register():
    Pool.register(
        product.Product,
        product.MinderestRecommendedPrice,
        rivals.ProductAppRivals,
        module='product_rivals_minderest', type_='model')
