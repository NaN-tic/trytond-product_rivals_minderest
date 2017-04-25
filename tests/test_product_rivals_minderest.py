# This file is part product_rivals_minderest module for Tryton.
# The COPYRIGHT file at the top level of this repository contains
# the full copyright notices and license terms.
import unittest
import os
from decimal import Decimal
from trytond.tests.test_tryton import ModuleTestCase, with_transaction
from trytond.tests.test_tryton import suite as test_suite
from trytond.modules.company.tests import create_company, set_company
from trytond.pool import Pool


class ProductRivalsMinderestTestCase(ModuleTestCase):
    'Test Product Rivals Netrivals module'
    module = 'product_rivals_minderest'

    @with_transaction()
    def test_minderest(self):
        'Minderest CSV data'
        pool = Pool()
        AppRivals = pool.get('product.app.rivals')
        Uom = pool.get('product.uom')
        Template = pool.get('product.template')

        company = create_company()
        with set_company(company):
            minderest, = AppRivals.create([{
                        'name': 'Minderest',
                        'app': 'minderest',
                        'app_uri': 'http://localhost',
                        'app_username': 'test',
                        'app_password': 'test',
                        }])

            unit, = Uom.search([
                    ('name', '=', 'Unit'),
                    ], limit=1)
            pt1, pt2 = Template.create([{
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
