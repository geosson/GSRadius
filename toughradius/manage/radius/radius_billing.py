#!/usr/bin/env python
# coding=utf-8
import datetime
from toughradius.manage.radius.radius_basic import  RadiusBasic
from toughradius.manage.events.settings import UNLOCK_ONLINE_EVENT
from toughlib.storage import Storage
from toughradius.manage import models
from toughlib import  utils, logger, dispatch
from toughradius.manage.settings import *
import decimal

decimal.getcontext().prec = 16
decimal.getcontext().rounding = decimal.ROUND_UP

class RadiusBilling(RadiusBasic):

    def __init__(self, dbengine=None,cache=None,aes=None,request=None):
        RadiusBasic.__init__(self, dbengine,cache,aes, request)
        self.bill_funcs = {
            PPTimes:self.bill_pptimes,
            BOTimes:self.bill_botimes,
            PPFlow:self.bill_ppflows,
            BOFlows:self.bill_boflows,
            FreeFee:self.bill_freefee
        }

    def billing(self, online):
        product = self.get_product_by_id(self.account.product_id)
        if not product:
            logger.error('product <%s> not exists' % self.account.product_id)
            return

        if product.product_policy not in (PPTimes,BOTimes,PPFlow,BOFlows):
            self.update_online(self.request.nas_addr,
                self.request.acct_session_id,
                billing_times=self.request.acct_session_time,
                input_total=self.get_input_total(),
                output_total=self.get_output_total())
        else:
            self.bill_funcs[product.product_policy](online, product)

    def bill_freefee(self, online, product):
        bill_type = self.get_account_attr('bill_type')
        if bill_type == FreeTimeLen:
            self.bill_botimes(online, product)
        elif bill_type == FreeFeeFlow:
            self.bill_boflows(online, product)


    def bill_pptimes(self,online,product):
        # 预付费时长
        logger.info('%s > Prepaid long time billing ' % self.account.account_number)
        user_balance = self.get_user_balance()
        sessiontime = decimal.Decimal(self.request.acct_session_time)
        billing_times = decimal.Decimal(online.billing_times)
        acct_times = sessiontime - billing_times
        if acct_times < 0:
            acct_times = 0
        fee_price = decimal.Decimal(product['fee_price'])
        usedfee = acct_times/decimal.Decimal(3600) * fee_price
        usedfee = actual_fee = int(usedfee.to_integral_value())
        balance = user_balance - usedfee
        
        if balance < 0 :  
            balance = 0
            actual_fee = user_balance
            
        self.update_billing(Storage(
            account_number = online.account_number,
            nas_addr = online.nas_addr,
            acct_session_id = online.acct_session_id,
            acct_start_time = online.acct_start_time,
            acct_session_time = self.request.acct_session_time,
            input_total = self.get_input_total(),
            output_total = self.get_output_total(),
            acct_times = int(acct_times.to_integral_value()),
            acct_flows = 0,
            acct_fee = usedfee,
            actual_fee = actual_fee,
            balance = balance,
            time_length = 0,
            flow_length = 0,
            is_deduct = 1,
            create_time = datetime.datetime.now().strftime( "%Y-%m-%d %H:%M:%S")
        ))
        
        if balance == 0 :
            dispatch.pub(UNLOCK_ONLINE_EVENT,
                online.account_number,online.nas_addr, online.acct_session_id,async=True)

    def bill_botimes(self,online, product):
        #买断时长
        logger.info('%s > Buyout long time billing ' % self.account.account_number)
        time_length = self.get_user_time_length()
        sessiontime = self.request.acct_session_time
        billing_times = online.billing_times
        acct_times = sessiontime - billing_times
        if acct_times < 0:
            acct_times = 0
        user_time_length = time_length - acct_times
        if user_time_length < 0 :
            user_time_length = 0

        self.update_billing(Storage(
            account_number = online.account_number,
            nas_addr = online.nas_addr,
            acct_session_id = online.acct_session_id,
            acct_start_time = online.acct_start_time,
            acct_session_time = self.request.acct_session_time,
            input_total = self.get_input_total(),
            output_total = self.get_output_total(),
            acct_times = acct_times,
            acct_flows = 0,
            acct_fee = 0,
            actual_fee = 0,
            balance = 0,
            time_length = user_time_length,
            flow_length = 0,
            is_deduct = 1,
            create_time = datetime.datetime.now().strftime( "%Y-%m-%d %H:%M:%S")
        ))
    
        if user_time_length == 0 :
            dispatch.pub(UNLOCK_ONLINE_EVENT,
                online.account_number,online.nas_addr, online.acct_session_id,async=True)

    def bill_ppflows(self, online, product):
        #预付费流量
        logger.info('%s > Prepaid flow billing '% self.account.account_number)
        user_balance = self.get_user_balance()
        output_total = decimal.Decimal(self.get_output_total())
        billing_output_total = decimal.Decimal(online.output_total)
        acct_flows = output_total - billing_output_total
        if acct_flows < 0:
            acct_flows = 0
        fee_price = decimal.Decimal(product.fee_price)
        usedfee = acct_flows/decimal.Decimal(1024) * fee_price
        usedfee = actual_fee = int(usedfee.to_integral_value())
        balance = user_balance - usedfee
        
        if balance < 0 :  
            balance = 0
            actual_fee = user_balance
            
        self.update_billing(Storage(
            account_number = online.account_number,
            nas_addr = online.nas_addr,
            acct_session_id = online.acct_session_id,
            acct_start_time = online.acct_start_time,
            acct_session_time = self.request.acct_session_time,
            input_total = self.get_input_total(),
            output_total = self.get_output_total(),
            acct_times = 0,
            acct_flows = int(acct_flows.to_integral_value()),
            acct_fee = usedfee,
            actual_fee = actual_fee,
            balance = balance,
            time_length = 0,
            flow_length = 0,
            is_deduct = 1,
            create_time = datetime.datetime.now().strftime( "%Y-%m-%d %H:%M:%S")
        ))
        
        if balance == 0:
            dispatch.pub(UNLOCK_ONLINE_EVENT,
                online.account_number,online.nas_addr, online.acct_session_id,async=True)

    def bill_boflows(self, online, product):
        #买断流量
        logger.info('%s > Buyout flow billing ' % self.account.account_number)
        flow_length = self.get_user_flow_length()
        output_total = self.get_output_total()
        billing_output_total = online.output_total
        acct_flows = output_total - billing_output_total
        if acct_flows < 0:
            acct_flows = 0
        user_flow_length = flow_length - acct_flows
        if user_flow_length < 0 :
            user_flow_length = 0
        self.update_billing(Storage(
            account_number = online.account_number,
            nas_addr = online.nas_addr,
            acct_session_id = online.acct_session_id,
            acct_start_time = online.acct_start_time,
            acct_session_time = self.request.acct_session_time,
            input_total = self.get_input_total(),
            output_total = self.get_output_total(),
            acct_times = 0,
            acct_flows = acct_flows,
            acct_fee = 0,
            actual_fee = 0,
            balance = 0,
            time_length = 0,
            flow_length = user_flow_length,
            is_deduct = 1,
            create_time = datetime.datetime.now().strftime( "%Y-%m-%d %H:%M:%S")
        ))
        
        if user_flow_length == 0 :
            dispatch.pub(UNLOCK_ONLINE_EVENT,
                online.account_number,online.nas_addr, online.acct_session_id,async=True)








