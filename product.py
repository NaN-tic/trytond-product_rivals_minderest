# encoding: utf-8
#This file is part product_rivals_minderest module for Tryton.
#The COPYRIGHT file at the top level of this repository contains
#the full copyright notices and license terms.
from trytond.model import ModelSQL, ModelView, fields
from trytond.pool import PoolMeta
from trytond.config import config

__all__ = ['Product', 'MinderestRecommendedPrice']

DIGITS = config.getint('product', 'price_decimal', default=4)


class Product:
    __name__ = 'product.product'
    __metaclass__ = PoolMeta
    minderest_recommended_prices = fields.One2Many(
        'product.minderest_recommended_price', 'product',
        'Minderest Recommended Price')


class MinderestRecommendedPrice(ModelSQL, ModelView):
    'Minderest Recommended Price'
    __name__ = 'product.minderest_recommended_price'
    product = fields.Many2One('product.product', 'Product', required=True)
    price = fields.Numeric('Price', digits=(16, DIGITS))
