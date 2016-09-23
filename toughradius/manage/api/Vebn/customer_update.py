#!/usr/bin/env python
#coding=utf-8
import traceback
from toughlib import utils, apiutils
from hashlib import md5
from toughlib.btforms import dataform
from toughlib.btforms import rules
from toughlib.permit import permit
from toughradius.manage.api.apibase import ApiHandler
from toughradius.manage import models


""" 客户资料修改，修改客户资料
"""

#customer_update_vform = dataform.Form(
#    dataform.Item("account_number", rules.not_null, description=u"用户认证账号"),
#    dataform.Item("product_id", rules.not_null, description=u"资费id"),
#    dataform.Item("password", rules.not_null, description=u"用户密码"),
#    dataform.Item("expire_date", rules.is_date, description=u"过期日期"),
#    dataform.Item("balance", rules.is_rmb, description=u"用户余额"),
#    dataform.Item("status", rules.is_number, description=u"用户状态"),
#    dataform.Item("address", description=u'the user address'))

@permit.route(r"/api/Vebn/customer/update")
class CustomerUpdateHandler(ApiHandler):
    """ @param:
        customer_name: str,
    """

    def get(self):
        self.post()

    def post(self):
        #form = customer_update_vform()
        try:
            request = self.parse_form_request()
        except apiutils.SignError, err:
            return self.render_sign_err(err)
        except Exception as err:
            return self.render_parse_err(err)



        try:
            account_number = request.get('account_number')

            if not account_number:
                return self.render_verify_err(msg="account_number is empty")

            account = self.db.query(models.TrAccount).filter_by(account_number=account_number).first()

            if not account:
                return self.render_verify_err(msg="%s is not existed" % account)

            password = request.get("password")
            product_id = request.get("product_id")
            expire_date = request.get("expire_date")
            status = request.get("status")
            #mobile = request.get("mobile")
            #email = request.get("email")


            if password:
                item = dataform.Item("password", rules.not_null, description=u"用户密码")
                if item.validate(password):
                    account.password = self.aes.encrypt(password)
                else:
                    return self.render_verify_err("password is error which is not satified")

            if product_id:
                item = dataform.Item("product_id", rules.not_null, description=u"资费id")
                if item.validate(product_id):
                    product = self.db.query(models.TrProduct).get(product_id)
                    if not product:
                        return self.render_verify_err(msg="this product_id : %s is not existed" % product_id)
                    account.product_id = product_id
                else:
                    return self.render_verify_err("product_id is error which is not satified")


            if expire_date:
                item = dataform.Item("expire_date", rules.is_date, description=u"过期日期")
                if item.validate(expire_date):
                    account.expire_date = expire_date
                else:
                    return self.render_verify_err("expire_date is error which is not satified")


            if status:
                item = dataform.Item("status", rules.is_number, description=u"用户状态")
                if item.validate(status):
                    account.status = status
                else:
                    return self.render_verify_err("status is error which is not satified")



            self.add_oplog(u'修改用户资料 %s' % account_number)
            self.db.commit()
            self.render_success()
        except Exception as err:
            self.render_unknow(err)
            import traceback
            traceback.print_exc()
            return















