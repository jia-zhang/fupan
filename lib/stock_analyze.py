import requests
import re
import time
import os
import json
from stock_util import StockUtil
from logger import Logger

class StockAnalyze():
    def __init__(self):
        #headers={'User-Agent':'Mozilla/5.0 (Windows NT 6.3; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/44.0.2403.157 Safari/537.36'}
        #detail_url = "http://money.finance.sina.com.cn/quotes_service/api/json_v2.php/CN_MarketData.getKLineData?symbol=sh000001&scale=240&ma=no&datalen=5"
        #resp = requests.get(detail_url)
        self.logger = Logger("StockAnalyze")
        self.util = StockUtil()
        #self.last_trading_day = eval(resp.text.replace('day','"day"').replace('open','"open"').replace('low','"low"').\
        #replace('high','"high"').replace('close','"close"').replace('volume','"volume"'))[-1]['day']

    def check_if_time_available(self):
        pass
    
    
    def get_volume_within_days(self,stock_list,day_num,volume_critiria):  
        '''
        过滤stock_list，返回day_num天前到现在，换手率超过volume_critiria的股票
        例如，get_volume_within_days(stock_list, 3, 20)表示返回3天内总换手超过20%的股票
        '''      
        ret = []
        for s in stock_list:
            volume = 0
            for i in range(day_num):
                volume = volume+self.util.get_volume(s,i)
            if volume>=volume_critiria:
                #self.logger.info("%s:%s"%(self.util.get_stock_name_from_id(s),volume))
                ret.append(s)
        return ret
        
    def first_round(self,stock_list,day_num,volume_critiria,increase_critiria):
        '''
        五天内的active stock
        '''
        self.logger.info("First round, get active volume>= %s and daily_increase>=%s stock in %s days"%(day_num,volume_critiria,increase_critiria))
        #days = [0,1,2,3,4]
        ret = []
        for day in range(day_num):
            self.logger.info("Day %s"%(day))
            tmp = a.get_active_stock(day,volume_critiria,increase_critiria)
            self.logger.info(tmp)
            self.logger.info("==============\n")
            ret.extend(tmp)
        self.logger.info("End of first round, found %s stocks"%(len(ret)))
        self.logger.info("============================\n\n")
        return ret
    
    def get_delta_within_days(self,stock_list,delta_day,delta_critiria):
        '''
        过滤stock_list，返回delta_day内涨幅>delta_critira的股票列表
        例如，get_delta_within_days(stock_list,3,20)表示拿到3天内涨幅>20%的股票列表
        '''
        self.logger.info("Start, get delta>%s stocks..."%(delta_critiria))
        ret=[]
        for s in stock_list:
            delta = self.util.get_delta(s,0-delta_day)
            #self.logger.info("%s:%s"%(s,delta))
            if(delta>delta_critiria and s not in ret):
                ret.append(s)
        self.logger.info("End, found %s stocks"%(len(ret)))
        self.logger.info("============================\n\n")
        return ret



if __name__ == '__main__':
    a = StockAnalyze()
    stock_list = a.util.get_stock_list_from_file('stocks.csv')
    #print(a.get_suspend_stocks())
    #tmp = a.first_round(5,10,9)
    #print(tmp)
    #tmp1 = a.get_delta_within_days(stock_list,3,20)
    tmp1 = a.get_volume_within_days(stock_list,3,20)    
    print(tmp1)
    #tmp2 = a.second_round(tmp,5,10)
    #print(tmp2)
    