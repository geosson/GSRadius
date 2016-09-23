#!/usr/bin/env python
#coding=utf-8

from toughlib.btforms import rules
from toughlib.btforms import dataform
from toughlib import utils, apiutils
from toughlib.permit import permit
from toughradius.manage.api.apibase import ApiHandler
from toughradius.manage import models

""" 产品套餐修改
"""

product_update_vform = dataform.Form(
    dataform.Item("product_id", rules.is_number2, description=u"资费id"),
    #dataform.Item("product_name", rules.len_of(4, 64), description=u"资费名称"),
    #dataform.Item("fee_price", rules.is_rmb, description=u"资费价格(元)"),
    #dataform.Item("input_max_limit", rules.is_number3, description=u"最大上行速率(Mbps)"),
    #dataform.Item("output_max_limit", rules.is_number3, description=u"最大下行速率(Mbps)"),
    title="api product update"
)

@permit.route(r"/api/Vebn/product/update")
class ProductUpdateHandler(ApiHandler):
    """ @param:
        product_id: str
    """

    def get(self):
        self.post()

    def post(self):
        form = product_update_vform()
        try:
            request = self.parse_form_request()
            if not form.validates(**request):
                return self.render_verify_err(form.errors)
        except apiutils.SignError, err:
            return self.render_sign_err(err)
        except Exception, err:
            return self.render_verify_err(err)


        try:
            product_id = request.get('product_id')
            product_name = request.get('product_name')
            fee_price = request.get('fee_price')
            input_max_limit = request.get('input_max_limit')
            output_max_limit = request.get('output_max_limit')
            if not product_id:
                return self.render_verify_err(msg="product_id must not be NULL")

            product = self.db.query(models.TrProduct).get(product_id)

            if not product:
                return self.render_verify_err(msg="product is not exist")

            if product_name:
                item = dataform.Item("product_name", rules.len_of(4, 64), description=u"资费名称")
                if item.validate(product_name):
                    product.product_name = product_name
                else:
                    return self.render_verify_err("product_name is error which is not satified")

            if fee_price:
                item = dataform.Item("fee_price", rules.is_rmb, description=u"资费价格(元)")
                if item.validate(fee_price):
                    product.fee_price = utils.yuan2fen(fee_price)
                else:
                    return self.render_verify_err("fee_price is error which is not satified")
#
            if input_max_limit:
                item = dataform.Item("input_max_limit", rules.is_number3, description=u"最大上行速率(Mbps)")
                if item.validate(input_max_limit):
                    product.input_max_limit = utils.mbps2bps(input_max_limit)
                else:
                    return self.render_verify_err("input_max_limit is error which is not satified")

            if output_max_limit:
                item = dataform.Item("output_max_limit", rules.is_number3, description=u"最大下行速率(Mbps)")
                if item.validate(output_max_limit):
                    product.output_max_limit = utils.mbps2bps(output_max_limit)
                else:
                    return self.render_verify_err("output_max_limit is error which is not satified")


            product.update_time = utils.get_currtime()

            self.db.commit()
            self.add_oplog(u'API修改资费信息:%s' % utils.safeunicode(product_id))
            self.render_success(msg=u'product update success')
        except Exception as err:
            self.render_unknow(err)















