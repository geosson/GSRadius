#!/usr/bin/env python
#coding=utf-8
import time
import traceback
from toughlib.btforms import dataform
from toughlib.btforms import rules
from toughlib import utils, apiutils, dispatch
from toughlib import db_cache as cache
from toughlib.permit import permit
from toughradius.manage.api.apibase import ApiHandler
from toughradius.manage import models
from toughradius.manage.events.settings import ACCOUNT_DELETE_EVENT
from toughradius.manage.settings import *
from hashlib import md5

""" 客户删除，删除客户资料及相关数据
"""

@permit.route(r"/api/Vebn/customer/delete")
class CustomerDeleteHandler(ApiHandler):
    """ @param:
        customer_name: str,
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
            account_number = request.get('account_number')

            if not account_number:
                return self.render_verify_err(msg="account_number is empty")

            account = self.db.query(models.TrAccount).filter_by(account_number=account_number).first()
            if not account:
                return self.render_verify_err(msg="account is not exists")

            for account in self.db.query(models.TrAccount).filter_by(customer_id=account.customer_id):
                self.db.query(models.TrAcceptLog).filter_by(account_number=account.account_number).delete()
                self.db.query(models.TrAccountAttr).filter_by(account_number=account.account_number).delete()
                self.db.query(models.TrBilling).filter_by(account_number=account.account_number).delete()
                self.db.query(models.TrTicket).filter_by(account_number=account.account_number).delete()
                self.db.query(models.TrOnline).filter_by(account_number=account.account_number).delete()
                self.db.query(models.TrAccount).filter_by(account_number=account.account_number).delete()
                self.db.query(models.TrCustomerOrder).filter_by(account_number=account.account_number).delete()
                self.add_oplog(u'删除用户账号%s' % (account.account_number))
                dispatch.pub(ACCOUNT_DELETE_EVENT, account.account_number, async=True)
                dispatch.pub(cache.CACHE_DELETE_EVENT,account_cache_key(account.account_number), async=True)

            customer = self.db.query(models.TrCustomer).filter_by(customer_id=account.customer_id).first()
            if customer:
                self.db.query(models.TrCustomer).filter_by(customer_id=account.customer_id).delete()


            self.add_oplog(u'删除用户资料 %s' % (account_number))
            self.db.commit()
            self.render_success()
        except Exception as err:
            self.render_unknow(err)
            import traceback
            traceback.print_exc()
            return















