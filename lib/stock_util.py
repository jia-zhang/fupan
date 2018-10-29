import requests
import re
import time
import os
import json
from logger import Logger

class StockUtil():
    def __init__(self):
        self.logger = Logger("StockUtil")
        self.stock_list_file = "stocks.csv"
        self.last_trading_day = self.get_last_trading_date()
        pass
    
    def get_valid_stock(self):
        return self.get_stock_list_from_file(self.stock_list_file)
    
    def check_file_and_read(self,file_name):
        if not os.path.exists(file_name):
            self.logger.info("File %s does not exist...Please check..."%(file_name))
            return ''
        with open(file_name,'r') as f:
            output = f.read()
        if output == "null":
            self.logger.info("File %s is null, please check..."%(file_name))
            return ''
        return output
    
    def get_static_file_from_id(self,stock_id):
        return "./data/static/%s.static.json"%(stock_id)
    
    def get_dynamic_file_from_id(self,stock_id):
        return "./data/dynamic/%s.json.d"%(stock_id)
    
    def get_stock_name_from_id(self,stock_id):
        file_name = self.get_static_file_from_id(stock_id)
        if not os.path.exists(file_name):
            return ''
        f = open(file_name,'r')
        json_output = json.load(f)
        f.close()
        return json_output[stock_id]['stock_name']
    
    def get_stock_list_from_file(self,file_name):
        '''
        从csv文件中获取列表，返回一个数组
        '''
        if not os.path.exists(file_name):
            self.logger.info("File %s does not exist, please check..."%(file_name))
            return []
        with open(file_name,'r') as f:
            output = f.read()
        return output.split(',')
    
    def get_last_trading_date(self):
        '''
        获取最近一次的交易日。获取上证指数的最后交易数据即可。
        '''
        #headers={'User-Agent':'Mozilla/5.0 (Windows NT 6.3; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/44.0.2403.157 Safari/537.36'}
        detail_url = "http://money.finance.sina.com.cn/quotes_service/api/json_v2.php/CN_MarketData.getKLineData?symbol=sh000001&scale=240&ma=no&datalen=5"
        resp = requests.get(detail_url)
        return eval(resp.text.replace('day','"day"').replace('open','"open"').replace('low','"low"').\
        replace('high','"high"').replace('close','"close"').replace('volume','"volume"'))[-1]['day']
    
    def get_suspend_stocks(self,stock_list):
        '''
        返回一个停牌的列表
        '''
        with open('valid_stock.csv','r') as f:
            output = f.read()
        s_list = output.split(',')
        ret = []
        for s in s_list:
            file_name = "./data/dynamic/%s.json.d"%(s)
            with open(file_name,'r') as f:
                output = f.read()
            if output == "null":
                ret.append(s)
                continue
            stock_detail = eval(output)
            if self.last_trading_day != stock_detail[-1]['day']:
                ret.append(s)
                self.logger.info(self.get_name_from_stock_id(s))
        return ret
    
    def get_delta(self,stock_id,day_num):
        '''
        获取day_num天前到目前收盘价的delta值，以%表示。
        如果day_num=0,表示今天的收盘价和今天收盘价的差值，所以会返回0
        '''
        file_name = self.get_dynamic_file_from_id(stock_id)
        output = self.check_file_and_read(file_name)
        if output=='':
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
        file_name = self.get_dynamic_file_from_id(stock_id)
        output = self.check_file_and_read(file_name)
        if output=='':
            return 0
        stock_detail = eval(output)
        if abs(-2+day_num)>len(stock_detail):
            self.logger.info("%s:No data on day %s"%(stock_id,day_num))
            return 0     
        if self.last_trading_day != stock_detail[-1]['day']:
            self.logger.info("Stock %s's last trading day not equals to sh000001's last trading day, please check..."%(stock_id))
            return 0   
        price_start = float(stock_detail[-2+day_num]['close'])
        #print(price_start)        
        price_end = float(stock_detail[-1+day_num]['close'])
        #print(price_end)
        lift_status = (price_end-price_start)*100/price_start
        return lift_status
    
    def get_volume(self,stock_id,day_num):
        '''
        获取某股票前day_num的当天换手率。day_num=0代表最后一天，day_num=1代表最后前一天
        '''
        file_name = self.get_dynamic_file_from_id(stock_id)
        output = self.check_file_and_read(file_name)
        if output == '':
            return 0
        stock_detail = eval(output)
        if abs(-1-day_num)>len(stock_detail):
            self.logger.info("%s:No data on day %s"%(stock_id,day_num))
            return 0
        volume = int(stock_detail[-1-day_num]['volume'])

        file_name = self.get_static_file_from_id(stock_id)
        if not os.path.exists(file_name):
            return 0
        f = open(file_name,'r')
        json_output = json.load(f)
        f.close()
        gb = json_output[stock_id]['float_shares']
        if(gb==0):
            self.logger.info("stock_id: %s,float_share is zero"%(stock_id))
        try:
            ret = volume*100/float(gb)
        except:
            self.logger.info("stock_id: %s,float_share is zero"%(stock_id))
        return ret
