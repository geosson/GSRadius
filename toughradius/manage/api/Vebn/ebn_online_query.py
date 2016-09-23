#!/usr/bin/env python
#coding=utf-8
import time
import traceback
from toughlib.btforms import dataform
from toughlib.btforms import rules
from toughlib import utils, apiutils, dispatch
from toughlib.permit import permit
from toughradius.manage.api.apibase import ApiHandler
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy import *
from sqlalchemy.ext.declarative import declarative_base
from toughradius.manage import models
import datetime

""" 在线用户查询
"""


@permit.route(r"/api/Vebn/online/current/query")
class OnlineHandler(ApiHandler):
    """ @param:
        client_id: id,
        type: 查询类型：  hour
                        day
                        month
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
            #client_id = request.get('client_id')
            node_id = request.get('node_id')
            account_number = request.get('account_number')
            framed_ipaddr = request.get('framed_ipaddr')
            mac_addr = request.get('mac_addr')
            nas_addr = request.get('nas_addr')
            opr_nodes = self.get_opr_nodes()
            _query = self.db.query(
                models.TrOnline.id,
                models.TrOnline.account_number,
                models.TrOnline.nas_addr,
                models.TrOnline.acct_session_id,
                models.TrOnline.acct_start_time,
                models.TrOnline.framed_ipaddr,
                models.TrOnline.mac_addr,
                models.TrOnline.nas_port_id,
                models.TrOnline.start_source,
                models.TrOnline.billing_times,
                models.TrOnline.input_total,
                models.TrOnline.output_total,
                models.TrCustomer.node_id,
                models.TrCustomer.realname
            ).filter(
                models.TrOnline.account_number == models.TrAccount.account_number,
                models.TrCustomer.customer_id == models.TrAccount.customer_id
            )
            if node_id:
                _query = _query.filter(models.TrCustomer.node_id == node_id)
            else:
                _query = _query.filter(models.TrCustomer.node_id.in_([i.id for i in opr_nodes]))

            if account_number:
                _query = _query.filter(models.TrOnline.account_number.like('%' + account_number + '%'))
            if framed_ipaddr:
                _query = _query.filter(models.TrOnline.framed_ipaddr == framed_ipaddr)
            if mac_addr:
                _query = _query.filter(models.TrOnline.mac_addr == mac_addr)
            if nas_addr:
                _query = _query.filter(models.TrOnline.nas_addr == nas_addr)

            _query = _query.order_by(models.TrOnline.acct_start_time.desc())

            colums = {'account_number':1, 'framed_ipaddr':5, 'mac_addr':6, 'acct_start_time':4, 'input_total':10, 'output_total':11,
                      'node_id':12, 'realname':13}
            online_data = {}

            for online in _query:
                if online:
                    online_data[online[1]] = {i:online[colums[i]] for i in colums.keys()}

            self.render_success(online=online_data)
        except Exception as err:
            self.render_unknow(err)
            import traceback
            traceback.print_exc()












