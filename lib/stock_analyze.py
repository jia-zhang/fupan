import requests
import re
import time
import os
import json

class StockAnalyze():
    def __init__(self):
        pass

    def get_delta(self,stock_id,day_num):
        '''
        获取某股票前day_num的当天涨跌幅。需要保证动态数据json文件里面有值，否则会报错(to be fixed)
        比如，获取前一天的get_delta('sz000002',-1)
        '''
        file_name = "./data/%s.json"%(stock_id)
        with open(file_name,'r') as f:
            output = f.read()
        stock_detail = eval(output)
        price_start = float(stock_detail[-2+day_num]['close'])
        print(price_start)        
        price_end = float(stock_detail[-1+day_num]['close'])
        print(price_end)
        lift_status = (price_end-price_start)*100/price_start
        return lift_status
    
    def get_volume(self,stock_id,day_num):
        '''
        获取某股票前day_num的当天换手率。
        '''
        file_name = "./data/%s.json"%(stock_id)
        if not os.path.exists(file_name):
            return 0
        with open(file_name,'r') as f:
            output = f.read()
        if output == "null":
            return 0
        stock_detail = eval(output)
        volume = int(stock_detail[-1+day_num]['volume'])

        file_name = "./data/%s.static.json"%(stock_id)
        if not os.path.exists(file_name):
            return 0
        f = open(file_name,'r')
        json_output = json.load(f)
        f.close()
        gb = json_output[stock_id]['float_shares']
        
        #print(volume)
        #print(gb)
        return volume*100/float(gb)
    
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
    #print(a.get_delta('sz000002',-2))

    #print(a.get_volume('sz000002',-1))
    with open('valid_stock.csv','r') as f:
        output = f.read()
    s_list = output.split(',')
    test = {}
    for s in s_list:
        try:
            volume = a.get_volume(s,0)
            test[s] = volume
        except:
            print("Exception on stock %s"%(s))
    i = 0
    tmp = [ v for v in sorted(test.values())]
    print(tmp)