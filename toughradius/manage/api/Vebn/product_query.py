#!/usr/bin/env python
#coding=utf-8
import time
import traceback
from toughlib.btforms import dataform
from toughlib.btforms import rules
from toughlib import utils, apiutils, dispatch
from toughlib.permit import permit
from toughradius.manage.api.apibase import ApiHandler
from toughradius.manage import models


@permit.route(r"/api/Vebn/product/query")
class ProductHandler(ApiHandler):
    """
    产品查询
    """

    def get(self):
        self.post()

    def post(self):
        try:
            request = self.parse_form_request()
        except apiutils.SignError, err:
            return self.render_sign_err(err)
        except Exception as err:
            return self.render_parse_err(err)

        try:
            product_id = request.get('product_id')
            products = self.db.query(models.TrProduct)
            if product_id:
                products = products.filter_by(id=product_id)

            product_datas = []
            #excludes = ['fee_period']
            for product in products:
                #product_data = { c.name : getattr(product, c.name) \
                #        for c in product.__table__.columns if c.name not in excludes}
                product_data = {
                    'id':product.id,
                    'product_name':product.product_name,
                    'fee_price':product.fee_price,
                    'input_max_limit':product.input_max_limit,
                    'output_max_limit':product.output_max_limit
                }
                product_datas.append(product_data)

            self.render_success(products=product_datas)
        except Exception as err:
            self.render_unknow(err)

