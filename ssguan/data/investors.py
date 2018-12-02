# -*- coding: utf-8 -*-
import datetime
import re
import time
import traceback

from ssguan import config
from ssguan.ignitor.web import webcli
from ssguan.ignitor.orm import properti
from ssguan.ignitor.utility import type, money
from ssguan.ignitor.orm.model import Model


class MoneyManStat(Model):
    
    @classmethod
    def meta_domain(cls):
        return config.MODULE_MONEY
    """
            统计周期
    """
    start_time = properti.DateTimeProperty("startTime", required=True)  # 统计开始时间
    end_time = properti.DateTimeProperty("endTime", required=True, validator=[properti.UniqueValidator('end_time', scope=['start_time'])])  # 统计结束时间
    """
           新增投资者数量 
    """
    mm_add_qty = properti.IntegerProperty("mmAddQty", required=True)  # 新增投资者数量    
    np_add_qty = properti.IntegerProperty("npAddQty", required=True)  # 新增自然人数量
    nonp_add_qty = properti.IntegerProperty("NoNpAddQty", required=True)  # 新增非自然人数量
    """
           期末投资者数量
    """
    mm_tmend_qty = properti.IntegerProperty("mmTmEndQty", required=True)  # 期末投资者数量
    np_tmend_qty = properti.IntegerProperty("npTmEndQty", required=True)  # 期末自然人数量
    np_tmend_a_qty = properti.IntegerProperty("npTmEndAQty", required=True)  # 期末自然人数量(已开A股)
    np_tmend_b_qty = properti.IntegerProperty("npTmEndQty", required=True)  # 期末自然人数量(已开B股)
    nonp_tmend_qty = properti.IntegerProperty("noNpTmEndQty", required=True)  # 期末非自然人数量
    nonp_tmend_a_qty = properti.IntegerProperty("noNpTmEndAQty", required=True)  # 期末非自然人数量(已开A股)
    nonp_tmend_b_qty = properti.IntegerProperty("noNpTmEndQty", required=True)  # 期末非自然人数量(已开B股) 
    """
            期末持仓投资者数量
    """
    mm_tmend_hold_qty = properti.IntegerProperty("mmTmEndHoldQty", required=True)  # 期末持仓投资者数量
    mm_tmend_hold_a_qty = properti.IntegerProperty("mmTmEndHoldAQty", required=True)  # 期末持仓投资者数量(持有A股的投资者)
    mm_tmend_hold_b_qty = properti.IntegerProperty("mmTmEndHoldBQty", required=True)  # 期末持仓投资者数量(持有B股的投资者) 
    """
            期间参与交易的投资者数量
    """
    mm_term_trade_qty = properti.IntegerProperty("mmTermTradeQty", required=True)  # 期间参与交易的投资者数量
    mm_term_trade_a_qty = properti.IntegerProperty("mmTermTradeAQty", required=True)  # 期间参与交易的投资者数量(A股交易投资者)
    mm_term_trade_b_qty = properti.IntegerProperty("mmTermTradeBQty", required=True)  # 期间参与交易的投资者数量(B股交易投资者)
    
    
def new_mms(date):
    mms = MoneyManStat()
    
    def fetch_one(date):
        datestr = type.datetime_to_str(date, fmt='%Y.%m.%d')
        options = {}
        options['method'] = 'POST'
        options['data'] = {'dateType':'',
                       'dateStr':datestr,
                        'channelIdStr':'6ac54ce22db4474abc234d6edbe53ae7'}
        response = webcli.http_fetch("http://www.chinaclear.cn/cms-search/view.action?action=china", options=options)
        return response
    def set_period(bs, mms):
        h2 = bs.find('h2', attrs={'class':'fl'})
        pat = re.compile(r"[\.]*([0-9.]*)-([0-9.]*)")
        xx = pat.search(h2.string).groups()
        st = type.str_to_datetime(xx[0], fmt='%Y.%m.%d')
        et = type.str_to_datetime(xx[1], fmt='%Y.%m.%d')
        mms.start_time = st
        mms.end_time = et
        return (st, et)
    def set_qty(bs, mms):
        row_delta = 0
        table = bs.find('table', attrs={"style":"WIDTH: 100%; BORDER-COLLAPSE: collapse"})
        if table is None:            
            table = bs.find('table', attrs={"style":"OVERFLOW-X: hidden; WORD-BREAK: break-all; WIDTH: 432pt"})
        if table is None:
            table = bs.find('table', attrs={"style":"width: 577px; border-collapse: collapse;"})
        if table is None:
            table = bs.find('table', attrs={"style":"width:100.0%;border-collapse:collapse;"})
        if table is None:
            table = bs.find('table', attrs={"style":"width: 100%; border-collapse: collapse;"})
        if table is None:
            table = bs.find('table', attrs={"style":"width: 432pt; word-break: break-all; overflow-x: hidden;"})
        if table is None:
            table = bs.find('table', attrs={"style":"width: 432pt; -ms-word-break: break-all; -ms-overflow-x: hidden;"})
        if table is None:
            table = bs.find('table', attrs={"style":"width: 599px; border-collapse: collapse;"})
        trs = table.find_all('tr')
        
        if trs[1 + row_delta].find_all('span')[-1].string == '投资者数（万）':
            row_delta += 1
        mms.mm_add_qty = money.kilostr_to_int(trs[1 + row_delta].find_all('span')[-1].string, times=10000)
#         mms.np_add_qty = moneyutils.kilostr_to_int(trs[2+row_delta].find_all('span')[-1].string, times=10000)
#         mms.nonp_add_qty = moneyutils.kilostr_to_int(trs[3+row_delta].find_all('span')[-1].string, times=10000)
#         mms.mm_tmend_qty = moneyutils.kilostr_to_int(trs[4+row_delta].find_all('span')[-1].string, times=10000)
#         mms.np_tmend_qty = moneyutils.kilostr_to_int(trs[5+row_delta].find_all('span')[-1].string, times=10000)
#         mms.np_tmend_a_qty = moneyutils.kilostr_to_int(trs[7+row_delta].find_all('span')[-1].string, times=10000)
#         mms.np_tmend_b_qty = moneyutils.kilostr_to_int(trs[8+row_delta].find_all('span')[-1].string, times=10000)
#         mms.nonp_tmend_qty = moneyutils.kilostr_to_int(trs[9+row_delta].find_all('span')[-1].string, times=10000)
#         mms.nonp_tmend_a_qty = moneyutils.kilostr_to_int(trs[11+row_delta].find_all('span')[-1].string, times=10000)
#         mms.nonp_tmend_b_qty = moneyutils.kilostr_to_int(trs[12+row_delta].find_all('span')[-1].string, times=10000)
#         if len(trs) >= 13+row_delta-1:
#             mms.mm_tmend_hold_qty = moneyutils.kilostr_to_int(trs[13+row_delta].find_all('span')[-1].string, times=10000)
#             mms.mm_tmend_hold_a_qty = moneyutils.kilostr_to_int(trs[15+row_delta].find_all('span')[-1].string, times=10000)
#             mms.mm_tmend_hold_b_qty = moneyutils.kilostr_to_int(trs[16+row_delta].find_all('span')[-1].string, times=10000)
#             mms.mm_term_trade_qty = moneyutils.kilostr_to_int(trs[17+row_delta].find_all('span')[-1].string, times=10000)
#             mms.mm_term_trade_a_qty = moneyutils.kilostr_to_int(trs[19+row_delta].find_all('span')[-1].string, times=10000)
#             mms.mm_term_trade_b_qty = moneyutils.kilostr_to_int(trs[20+row_delta].find_all('span')[-1].string, times=10000)
    response = fetch_one(date)
    bs = response.to_unibs()
    set_period(bs, mms)
    set_qty(bs, mms)
    return mms
        
def fetch_all():
    
    start_date = type.str_to_datetime('2015.01.06' , fmt='%Y.%m.%d')
#     start_date = type.str_to_datetime('2015.09.21' , fmt='%Y.%m.%d')
#     start_date = type.str_to_datetime('2017.02.06' , fmt='%Y.%m.%d')
#     start_date = type.str_to_datetime('2017.05.08' , fmt='%Y.%m.%d')
#     start_date = type.str_to_datetime('2016.04.25' , fmt='%Y.%m.%d')
#     start_date = type.str_to_datetime('2016.07.04' , fmt='%Y.%m.%d')
#     start_date = type.str_to_datetime('2016.08.15' , fmt='%Y.%m.%d')
#     start_date = type.str_to_datetime('2016.10.10' , fmt='%Y.%m.%d')
#     start_date = type.str_to_datetime('2016.10.24' , fmt='%Y.%m.%d')
#     start_date = type.str_to_datetime('2017.01.23' , fmt='%Y.%m.%d')
#     start_date = type.str_to_datetime('2016.12.09' , fmt='%Y.%m.%d')
    start_date = type.str_to_datetime('2017.09.11' , fmt='%Y.%m.%d')
    end_date = type.str_to_datetime('2017.10.01' , fmt='%Y.%m.%d')
    mmses = []
    while start_date <= end_date:
        try:
            time.sleep(0.2)
            mms = new_mms(start_date)
            mmses.append(mms)
            start_date += datetime.timedelta(days=7)
        except:
            print (start_date)
            traceback.print_exc()
            start_date += datetime.timedelta(days=7)
    print (len(mmses))
    return mmses    

mmses = fetch_all()
with open("d:/moneymans_original.csv", "w") as f:
    f.writelines('start_date,end_date,moneymans\n')
    for mms in mmses:
        f.writelines("%s,%s,%i\n" % (type.datetime_to_str(mms.start_time, fmt='%Y-%m-%d'), type.datetime_to_str(mms.end_time, fmt='%Y-%m-%d'), mms.mm_add_qty))
    f.close()
        
with open("d:/moneymans_dealed.csv", "w") as f:
    f.writelines('start_date,moneymans\n')
    for mms in mmses:
        t = mms.end_time - mms.start_time + datetime.timedelta(days=1)
        tmp = mms.start_time
        while tmp <= mms.end_time:
            avg = mms.mm_add_qty / t.days           
            f.writelines("%s,%.2f\n" % (type.datetime_to_str(tmp, fmt='%Y-%m-%d'), avg))
            tmp += datetime.timedelta(days=1)
            
    f.close()
    






