# This file is part product_rivals_minderest module for Tryton.
# The COPYRIGHT file at the top level of this repository contains
# the full copyright notices and license terms.
import urllib2
import base64
import csv
from decimal import Decimal
from trytond.pool import Pool, PoolMeta
from trytond.pyson import Eval

__all__ = ['ProductAppRivals']


class ProductAppRivals:
    __name__ = 'product.app.rivals'
    __metaclass__ = PoolMeta

    @classmethod
    def __setup__(cls):
        super(ProductAppRivals, cls).__setup__()
        required = (Eval('app') in ['minderest', 'minderest_recommended_price'])
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
        res.append(('minderest_recommended_price', 'Minderest Recommended Price'))
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

    def update_prices_minderest_recommended_price(self):
        username = self.app_username
        password = self.app_password
        request = urllib2.Request(self.app_uri)
        base64string = base64.encodestring('%s:%s' % (username, password)).replace('\n', '')
        request.add_header("Authorization", "Basic %s" % base64string)
        result = urllib2.urlopen(request)
        rows = result.read().decode('iso-8859-1').encode('utf8')
        self.minderest_recommended_prices(rows)

    def minderest_recommended_prices(self, rows):
        RecommendedPrice = Pool().get('product.minderest_recommended_price')
        has_header = True
        csv_dict = {}
        to_save = []

        spamreader = csv.reader(rows.split('\n'), delimiter=';')
        field_names_list = spamreader.next()

        for row in csv.reader(rows.split('\n'), delimiter=';'):
            if not row:
                continue
            for i in xrange(0,len(field_names_list)):
                csv_dict[field_names_list[i]] = row[i]
            if has_header:
                has_header = False
                continue

            recommended_price = self.get_recomended_price(csv_dict)
            if recommended_price:
                to_save.append(recommended_price)

        RecommendedPrice.save(to_save)

    def recommended_price_domain(self, product):
        return [('product', '=', product)]

    def get_recomended_price(self, csv_dict):
        pool = Pool()
        RecommendedPrice = pool.get('product.minderest_recommended_price')
        Product = Pool().get('product.product')

        products = Product.search([('code', '=', str(csv_dict['g:mpn']))], limit=1)
        if not products:
            return
        product, = products

        recommended_prices = RecommendedPrice.search(
            self.recommended_price_domain(product), limit=1)
        price = Decimal(csv_dict[
            'price_recommended_tax_excluded']).quantize(Decimal(str(10**-2)))
        if recommended_prices:
            recommended_price, = recommended_prices
            recommended_price.price = price
        else:
            recommended_price = RecommendedPrice()
            recommended_price.product = product
            recommended_price.price = price
        return recommended_price
