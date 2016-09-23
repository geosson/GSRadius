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

""" 日志用户查询查询，
"""


@permit.route(r"/api/Vebn/ticket/query")
class TicketHandler(ApiHandler):
    """

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
            node_id = request.get('node_id')
            #client_id = request('client_id')
            account_number = request.get('account_number')
            framed_ipaddr = request.get('framed_ipaddr')
            mac_addr = request.get('mac_addr')
            query_time = request.get('query_time')
            realname = request.get('realname')
            opr_nodes = self.get_opr_nodes()
            _query = self.db.query(
                models.TrTicket.id,
                models.TrTicket.account_number,
                models.TrTicket.nas_addr,
                models.TrTicket.acct_session_id,
                models.TrTicket.acct_start_time,
                models.TrTicket.acct_stop_time,
                models.TrTicket.acct_input_octets,
                models.TrTicket.acct_output_octets,
                models.TrTicket.acct_input_gigawords,
                models.TrTicket.acct_output_gigawords,
                models.TrTicket.framed_ipaddr,
                models.TrTicket.mac_addr,
                models.TrTicket.nas_port_id,
                models.TrCustomer.node_id,
                models.TrCustomer.realname
            ).filter(
                models.TrTicket.account_number == models.TrAccount.account_number,
                models.TrCustomer.customer_id == models.TrAccount.customer_id
            )

            if node_id:
                _query = _query.filter(models.TrCustomer.node_id == node_id)
            else:
                _query = _query.filter(models.TrCustomer.node_id.in_([i.id for i in opr_nodes]))
            if account_number:
                _query = _query.filter(models.TrTicket.account_number.like('%' + account_number + '%'))
            if framed_ipaddr:
                _query = _query.filter(models.TrTicket.framed_ipaddr == framed_ipaddr)
            if mac_addr:
                _query = _query.filter(models.TrTicket.mac_addr == mac_addr)
            if realname:
                _query = _query.filter(models.TrCustomer.realname == realname)
            if query_time:
                _start = '%s 00:00:00' %query_time
                _end = '%s 23:59:59' %query_time
                _query = _query.filter(models.TrTicket.acct_start_time >= _start,
                                       models.TrTicket.acct_start_time <= _end)

            _query = _query.order_by(models.TrTicket.acct_start_time.desc())

            colums = {'account_number':1, 'framed_ipaddr':10, 'mac_addr':11, 'acct_start_time':4, 'acct_stop_time':5, 'acct_input_octets':6, 'acct_output_octets':7,
                      'node_id':13, 'realname':14}
            ticket_data = [] 

            for ticket in _query:
                if ticket:
                    ticket_data.append({i:ticket[colums[i]] for i in colums.keys()})

            self.render_success(ticket=ticket_data)
        except Exception as err:
            self.render_unknow(err)
            import traceback
            traceback.print_exc()






