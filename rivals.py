# This file is part product_rivals_minderest module for Tryton.
# The COPYRIGHT file at the top level of this repository contains
# the full copyright notices and license terms.
import urllib2
import base64
import csv
from decimal import Decimal
from trytond.config import config
from trytond.pool import PoolMeta
from trytond.pyson import Eval

__all__ = ['ProductAppRivals']

DIGITS = config.getint('product', 'price_decimal', default=4)


class ProductAppRivals:
    __name__ = 'product.app.rivals'
    __metaclass__ = PoolMeta

    @classmethod
    def __setup__(cls):
        super(ProductAppRivals, cls).__setup__()

        required = (Eval('app') == 'minderest')
        if 'required' in cls.app_username.states:
            cls.app_username.states['required'] |= required
        else:
            cls.app_username.states['required'] = required
        if 'required' in cls.app_password.states:
            cls.app_password.states['required'] |= required
        else:
            cls.app_password.states['required'] = required

    @classmethod
    def get_app(cls):
        res = super(ProductAppRivals, cls).get_app()
        res.append(('minderest', 'Minderest'))
        return res

    def update_prices_minderest(self):
        username = self.app_username
        password = self.app_password
        request = urllib2.Request(self.app_uri)
        base64string = base64.encodestring('%s:%s' % (username, password)).replace('\n', '')
        request.add_header("Authorization", "Basic %s" % base64string)
        result = urllib2.urlopen(request)
        rows = result.read().decode('iso-8859-1').encode('utf8')

        self.minderest_rivals(rows)

    def minderest_rivals(self, rows):
        has_header = True
        rivals_cols = {}
        values = {}
        for row in csv.reader(rows.split('\n'), delimiter=';'):
            if not row:
                continue
            if has_header:
                column = 0
                for r in row:
                    if r.startswith('price '):
                        # get rival name from second position
                        name = r.split(' ')[1]
                        rivals_cols[name] = column
                    column += 1
                has_header = False
                continue

            code = row[1]
            rivals = {}
            rival_prices = []
            for k, v in rivals_cols.iteritems():
                rival_name = k
                rival_price = row[v].replace(',', '.')
                if not rival_price:
                    continue
                rprice = Decimal(rival_price)
                rivals[rival_name] = rprice
                rival_prices.append(rprice)
            if not rival_prices:
                continue
            min_price = min(rival_prices)
            max_price = max(rival_prices)
            values[code] = {
                'rivals': rivals,
                'min_price': Decimal(min_price),
                'max_price': Decimal(max_price),
                }

        self.create_rivals(values)
