import requests
import re
import time
from stock_query import StockQuery

class StockAnalyze():
    def __init__(self):
        pass
    
    def get_lift_high(self,time_range,top_n):
        q = StockQuery()
        last_trading_date = q.get_last_trading_date()
        s_list = q.get_stock_list_from_file('stocks.csv')
        status = []
        i=0
        for s in s_list:
            stock_detail = eval(q.get_stock_detail(s,240,time_range))
            price_open = float(stock_detail[0]['open'])
            price_close = float(stock_detail[-1]['close'])
            lift_status = (price_close-price_open)*100/price_open
            #today = str(datetime.date.today())
            if(stock_detail[-1]['day']==last_trading_date):
                status.append("%s:%s"%(s,lift_status))
            i=i+1
            #time.sleep(1)
            if i==100:
                break
        with open('price_change.txt','w') as f:
            f.write(",".join(status))

if __name__ == '__main__':
    a = StockAnalyze()
    a.get_lift_high(10,10)