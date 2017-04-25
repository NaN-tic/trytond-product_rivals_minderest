# This file is part product_rivals_minderest module for Tryton.
# The COPYRIGHT file at the top level of this repository contains
# the full copyright notices and license terms.
import unittest
import os
from decimal import Decimal
from trytond.tests.test_tryton import ModuleTestCase
from trytond.tests.test_tryton import suite as test_suite
from trytond.tests.test_tryton import POOL, DB_NAME, USER, CONTEXT
from trytond.transaction import Transaction


class ProductRivalsMinderestTestCase(ModuleTestCase):
    'Test Product Rivals Netrivals module'
    module = 'product_rivals_minderest'

    def setUp(self):
        super(ProductRivalsMinderestTestCase, self).setUp()
        self.app_rivals = POOL.get('product.app.rivals')
        self.uom = POOL.get('product.uom')
        self.template = POOL.get('product.template')

    def test0010minderest(self):
        'Minderest CSV data'
        with Transaction().start(DB_NAME, USER,
                context=CONTEXT) as transaction:
            minderest, = self.app_rivals.create([{
                        'name': 'Minderest',
                        'app': 'minderest',
                        'app_uri': 'http://localhost',
                        'app_username': 'test',
                        'app_password': 'test',
                        }])

            unit, = self.uom.search([
                    ('name', '=', 'Unit'),
                    ], limit=1)
            pt1, pt2 = self.template.create([{
                        'name': 'Product 1',
                        'type': 'goods',
                        'list_price': Decimal(20),
                        'cost_price': Decimal(10),
                        'default_uom': unit.id,
                        'products': [('create', [{
                                        'code': 'PROD1',
                                        }])]
                        }, {
                        'name': 'Product 2',
                        'type': 'goods',
                        'list_price': Decimal(20),
                        'cost_price': Decimal(10),
                        'default_uom': unit.id,
                        'products': [('create', [{
                                        'code': 'PROD2',
                                        }])]
                        }])

            minderestfile = os.path.join(
                os.path.dirname(__file__), 'minderest.csv')
            rows = open(minderestfile, 'r').read()
            minderest.minderest_rivals(rows)

            self.assertEqual(pt1.list_price_min_rival, Decimal('9.08'))
            self.assertEqual(pt1.list_price_max_rival, Decimal('10.34'))
            self.assertEqual(pt2.list_price_min_rival, Decimal('17.63'))
            self.assertEqual(pt2.list_price_max_rival, Decimal('17.88'))

            p1, = pt1.products
            rival1, rival2 = p1.rivals
            self.assertEqual(rival1.price, Decimal('9.08'))
            self.assertEqual(rival2.price, Decimal('10.34'))

            p2, = pt2.products
            rival1, rival2 = p2.rivals
            self.assertEqual(rival1.price, Decimal('17.63'))
            self.assertEqual(rival2.price, Decimal('17.88'))

def suite():
    suite = test_suite()
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(
            ProductRivalsMinderestTestCase))
    return suite
