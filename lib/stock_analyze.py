import requests
import re
import time
import os
from stock_query import StockQuery

class StockAnalyze():
    def __init__(self):
        pass

    def get_delta(self,stock_id,day_num):
        file_name = "./data/%s.json"%(stock_id)
        with open(file_name,'r') as f:
                output = f.read()
        stock_detail = eval(output)
        price_open = float(stock_detail[-1-day_num]['close'])
        price_close = float(stock_detail[-1]['close'])
        lift_status = (price_close-price_open)*100/price_open
        return lift_status
    
    def get_volume(self,stock_id,day_num):
        q = StockQuery()
        gb = q.get_stock_basic(stock_id,"test")
        print(gb)
        file_name = "./data/%s.json"%(stock_id)
        with open(file_name,'r') as f:
                output = f.read()
        stock_detail = eval(output)
        volume = int(stock_detail[-1-day_num]['volume'])
        return volume/float(gb)
    
    def get_lift_high(self,top_n):
        q = StockQuery()
        last_trading_date = q.get_last_trading_date()
        #s_list = q.get_stock_list_from_file('stocks.csv')
        status = []
        i=0
        for file_name in os.listdir('./data'):
            with open("./data/%s"%(file_name),'r') as f:
                output = f.read()
            stock_detail = eval(output)
            price_open = float(stock_detail[0]['open'])
            price_close = float(stock_detail[-1]['close'])
            lift_status = (price_close-price_open)*100/price_open
            #today = str(datetime.date.today())
            if(stock_detail[-1]['day']==last_trading_date):
                status.append("%s:%s"%(file_name.replace('.json',''),lift_status))
            i=i+1
            #time.sleep(1)
            if i==100:
                break
        with open('price_change.txt','w') as f:
            f.write(",".join(status))

if __name__ == '__main__':
    a = StockAnalyze()
    #print(a.get_delta('sz000002',9))
    print(a.get_volume('sz000002',4))