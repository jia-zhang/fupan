import requests
import re
import time
import os
import json

class StockAnalyze():
    def __init__(self):
        #headers={'User-Agent':'Mozilla/5.0 (Windows NT 6.3; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/44.0.2403.157 Safari/537.36'}
        detail_url = "http://money.finance.sina.com.cn/quotes_service/api/json_v2.php/CN_MarketData.getKLineData?symbol=sh000001&scale=240&ma=no&datalen=5"
        resp = requests.get(detail_url)
        self.last_trading_day = eval(resp.text.replace('day','"day"').replace('open','"open"').replace('low','"low"').\
        replace('high','"high"').replace('close','"close"').replace('volume','"volume"'))[-1]['day']

    def check_if_time_available(self):
        pass
    
    def get_suspend_stocks(self):
        '''
        返回一个停牌的列表
        '''
        with open('valid_stock.csv','r') as f:
            output = f.read()
        s_list = output.split(',')
        ret = []
        for s in s_list:
            file_name = "./data/%s.json"%(s)
            with open(file_name,'r') as f:
                output = f.read()
            if output == "null":
                ret.append(s)
                continue
            stock_detail = eval(output)
            if self.last_trading_day != stock_detail[-1]['day']:
                ret.append(s)
                print(self.get_name_from_id(s))
        return ret

    def get_name_from_id(self,stock_id):
        file_name = "./data/%s.static.json"%(stock_id)
        if not os.path.exists(file_name):
            return 0
        f = open(file_name,'r')
        json_output = json.load(f)
        f.close()
        return json_output[stock_id]['stock_name']

    def get_delta(self,stock_id,day_num):
        '''
        获取day_num天前到目前收盘价的delta值，以%表示。
        如果day_num=0,表示今天的收盘价和今天收盘价的差值，所以会返回0
        '''
        file_name = "./data/%s.json"%(stock_id)
        if not os.path.exists(file_name):
            return 0
        with open(file_name,'r') as f:
            output = f.read()
        if output == "null":
            return 0
        stock_detail = eval(output)
        if abs(-1+day_num)>len(stock_detail):
            #print("%s:No data on day %s"%(stock_id,day_num))
            return 0
        if self.last_trading_day != stock_detail[-1]['day']:
            #print("停牌或者怎样了%s"%(stock_id))
            return 0
        price_start = float(stock_detail[-1+day_num]['close'])
        #print(price_start)        
        price_end = float(stock_detail[-1]['close'])
        #print(price_end)
        lift_status = (price_end-price_start)*100/price_start
        return lift_status
        

    def get_increase_amount(self,stock_id,day_num):
        '''
        获取某股票前day_num的当天涨跌幅。需要保证动态数据json文件里面有值，否则会报错(to be fixed)
        比如，获取前一天的get_increase_amount('sz000002',-1)
        '''
        file_name = "./data/%s.json"%(stock_id)
        if not os.path.exists(file_name):
            return 0
        with open(file_name,'r') as f:
            output = f.read()
        if output == "null":
            return 0
        stock_detail = eval(output)
        if abs(-2+day_num)>len(stock_detail):
            #print("%s:No data on day %s"%(stock_id,day_num))
            return 0     
        if self.last_trading_day != stock_detail[-1]['day']:
            #print("停牌或者怎样了%s"%(stock_id))
            return 0   
        price_start = float(stock_detail[-2+day_num]['close'])
        #print(price_start)        
        price_end = float(stock_detail[-1+day_num]['close'])
        #print(price_end)
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
        if abs(-1+day_num)>len(stock_detail):
            #print("%s:No data on day %s"%(stock_id,day_num))
            return 0
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
    
    def get_active_stock(self,day_num,volume_critiria,increase_critiria):
        with open('valid_stock.csv','r') as f:
            output = f.read()
        s_list = output.split(',')
        ret = []
        for s in s_list:
            try:
                volume = a.get_volume(s,0-day_num)
                delta = a.get_increase_amount(s,0-day_num)
                if volume>=volume_critiria and delta>=increase_critiria:
                    print("%s:%s:%s"%(a.get_name_from_id(s),volume,delta))
                    ret.append(s)
            except Exception as e:
                print(e)
                print(s)
        return ret
        
    def first_round(self,day_num,volume_critiria,increase_critiria):
        '''
        五天内的active stock
        '''
        print("First round, get active volume>= %s and daily_increase>=%s stock in %s days"%(day_num,volume_critiria,increase_critiria))
        #days = [0,1,2,3,4]
        ret = []
        for day in range(day_num):
            print("Day %s"%(day))
            tmp = a.get_active_stock(day,volume_critiria,increase_critiria)
            print(tmp)
            print("==============\n")
            ret.extend(tmp)
        print("End of first round, found %s stocks"%(len(ret)))
        print("============================\n\n")
        return ret
    
    def second_round(self,stock_list,delta_critiria):
        print("Second round, get delta>%s stocks..."%(delta_critiria))
        ret=[]
        for s in stock_list:
            delta = self.get_delta(s,-5)
            print("%s:%s"%(s,delta))
            if(delta>delta_critiria and s not in ret):
                ret.append(s)
        print("End of second round, found %s stocks"%(len(ret)))
        print("============================\n\n")
        return ret



if __name__ == '__main__':
    a = StockAnalyze()
    #print(a.get_suspend_stocks())
    tmp = a.first_round(5,10,9)
    print(tmp)
    print(a.second_round(tmp,15))
    