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

""" 在线用户分析查询，
"""


@permit.route(r"/api/Vebn/online/analysis/query")
class CustomerAccountsHandler(ApiHandler):
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
            client_id = request.get('client_id')
            node_id = request.get('node_id')
            #mode = request.get('mode')
            #start_time = request.get('start_time')
            #end_time = request.get('end_time')
            product_id = request.get('product_id')
            query_time = request.get('query_time')

            #if not node_id:
            #    return self.render_parse_err("lack of start_time or mode or end_time or client_id")
            if not query_time:
                query_time = (datetime.datetime.now()).strftime("%Y-%m-%d")

            start_time = '%s 00' %query_time
            end_time = '%s 24'  %query_time

            try:
                db = None
                database = 'mysql://raduser:radpwd@127.0.0.1:3306/raddblog?charset=utf8'
                engine = create_engine(database)
                session = sessionmaker(bind=engine)
                db = session()

                onlines = db.query(EBNOnlineStat.client_id,
                                   EBNOnlineStat.node_id,
                                   EBNOnlineStat.product_id,
                                   EBNOnlineStat.total,
                                   EBNOnlineStat.stat_time).filter(EBNOnlineStat.stat_time >= start_time,
                                                                   EBNOnlineStat.stat_time < end_time)

                if client_id:
                    onlines = onlines.filter(EBNOnlineStat.client_id==client_id)
                if product_id:
                    onlines = onlines.filter(EBNOnlineStat.product_id==product_id)
            except Exception, e:
                import traceback
                traceback.print_exc()
                return self.render_verify_err(msg="some wrong with query: %s" % str(e))
            finally:
                if db:
                    db.close()

            online_data = []
            for i in onlines:
                data = {'client_id':i[0], 'node_id':i[1], 'product_id':i[2], 'total':i[3], 'date':i[4][:-3], 'time':i[4][-2:]}
                online_data.append(data)
            
            self.render_success(online=online_data)
        except Exception as err:
            self.render_unknow(err)
            import traceback
            traceback.print_exc()



DeclarativeBase = declarative_base()


class EBNOnlineStat(DeclarativeBase):

    __tablename__ = 'ebn_online_stat'

    __table_args__ = {}

    id = Column('id', INTEGER(), primary_key=True, nullable=False,doc=u"id")
    client_id = Column('client_id', INTEGER(), nullable=False,doc=u"客户id")
    node_id = Column('node_id', INTEGER(),  nullable=False,doc=u"区域id")
    product_id = Column('product_id', INTEGER(), nullable=False,doc=u"product id")
    total = Column(u'total', INTEGER(),doc=u"在线数")
    stat_time = Column('stat_time', Unicode(length=19), nullable=False,doc=u"时间")












