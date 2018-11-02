# -*- coding: utf-8 -*-  
import requests
import re
import time
import os
import json
import random
import datetime
import subprocess
from logger import Logger
from stock_util import StockUtil

class StockDump():
    def __init__(self):
        #self.stock_list_url = "http://quote.eastmoney.com/stocklist.html"
        self.logger = Logger("StockDump")
        with open('last_dump_date.txt','r') as f:
            self.last_dump_date = f.read()
        self.stock_list_file = 'stocks.csv'
        self.util = StockUtil()   

    
    def get_stock_list(self):
        '''
        应该只需要调用一次，以后统一用valid_stock.csv
        '''
        resp = requests.get("http://quote.eastmoney.com/stocklist.html")
        resp.encoding = 'gb2312'
        s = r'<li><a target="_blank" href="http://quote.eastmoney.com/(.*?).html">'
        pat = re.compile(s)
        codes = pat.findall(resp.text)
        return codes

    def save_stock_list(self,file_name):
        '''
        同上
        '''
        ret = []
        all_stocks = self.get_stock_list()
        for n in all_stocks:
            if n.startswith('sz00') or n.startswith('sh60') or n.startswith('sz300'):
                ret.append(n)
        with open(file_name,'w') as f:
            f.write(",".join(ret))
       
    def get_stock_detail(self,stock_id,time_range,count,retry_num=3):
        '''
        获取某股票在time_range内的动态数据，开盘价，收盘价之类。
        统一从新浪拿，每天15：00以后拿一次就可以。
        '''
        #headers={'User-Agent':'Mozilla/5.0 (Windows NT 6.3; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/44.0.2403.157 Safari/537.36'}
        ret = ''
        detail_url = ("http://money.finance.sina.com.cn/quotes_service/api/json_v2.php/CN_MarketData.getKLineData?"
                    "symbol=%s&scale=%s&ma=no&datalen=%s"
        )%(stock_id,time_range,count)
        #self.logger.info(detail_url)
        try:
            resp = requests.get(detail_url,timeout=60)
            if resp.status_code!=200:
                request.raise_for_status()
            ret = resp.text.replace('day','"day"').replace('open','"open"').replace('low','"low"')\
            .replace('high','"high"').replace('close','"close"').replace('volume','"volume"')
        except requests.exceptions.ConnectionError as e:
            self.logger.info("Connection error...exit")
            return ret
        except:
            #html=None
            if retry_num>0:
            #如果不是200就重试，每次递减重试次数
                self.logger.info("Non 200 respose, retry. Status_code=%s"%(resp.status_code))
                return self.get_stock_detail(url,stock_id,time_range,count,retry_num-1)
        return ret    
    
    def dump_stock_dynamic(self,time_range,count,force=1):
        '''
        Get stock dynamic info, 10 days open,high,low,close,volume
        此函数在每天15：00之后调用一次即可。会存放在代码.dynamic.json文件里面。
        新浪在多次请求后会timeout，多次调用次函数作为workaround.
        '''
        #cur_time = time.localtime().tm_hour
        self.logger.info(self.last_dump_date)
        self.logger.info(self.util.get_last_trading_date())
        if self.last_dump_date == self.util.get_last_trading_date():
            self.logger.info("No new info needs to be dumped, today is %s, last_dump_date is %s, last_trading_date is %s"%(time.strftime('%Y-%m-%d',time.localtime(time.time())),self.last_dump_date,self.get_last_trading_date()))
            return
        s_list = self.util.get_valid_stocks()
        for s in s_list:
            self.logger.info("Dumping stock dynamic %s..."%(s))
            file_name = self.util.get_dynamic_file_from_id(s)
            #self.logger.info(file_name)
            if (force==0 and os.path.exists(file_name)):
                self.logger.info("%s already exists, skip"%(s))
                continue
            stock_detail = self.get_stock_detail(s,time_range,count)
            with open(file_name,'w') as f:
                f.write(stock_detail)
            
    def dump_stock_static(self,stock_list,force=0):
        '''
        Get some very basic static information from xueqiu.com
        if force==1, will overwrite exists json file, please be careful
        '''
        headers={'User-Agent':'Mozilla/5.0 (Windows NT 6.3; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/44.0.2403.157 Safari/537.36'}
        re_fload_shares = re.compile(r'"float_shares":(\d*?),')
        re_stock_name = re.compile(r'"name":(.*?),')
        re_market_capital = re.compile(r'"market_capital":(.*?),')
        for s in stock_list:
            self.logger.info("Dumping stock static %s..."%(s))
            file_name = self.util.get_static_file_from_id(s)
            if (force==0 and os.path.exists(file_name)):
                self.logger.info("%s already exists, skip"%(s))
                continue
            try:
                master_dict = {}
                resp = requests.get("https://xueqiu.com/S/%s"%(s),headers=headers)
                if (resp.status_code==404):
                    self.logger.info("Get code 404 on stock %s"%(s))                    
                    continue
                elif(resp.status_code!=200):
                    self.logger.info("Get code %s on stock %s"%(resp.status_code,s))
                    continue
                resp.encoding = 'utf-8'            
                stock_dict = {}
                stock_dict['float_shares'] = str(re_fload_shares.findall(resp.text)[0])  
                stock_dict['stock_name'] = str(re_stock_name.findall(resp.text)[0])
                stock_dict['market_capital'] = str(re_market_capital.findall(resp.text)[0])
                master_dict[s] = stock_dict
                with open(file_name,'w') as f:
                    f.write(json.dumps(master_dict))
            except:
                self.logger.info("exception on stock %s!"%(s))
    
    def zip_dynamic(self,folder):
        cur_date = datetime.datetime.now().strftime('%Y_%m_%d')
        zip_cmd = "7z a dynamic_%s.zip %s"%(cur_date,folder)
        return subprocess.Popen(zip_cmd,shell=True) 
    
    def upload_dynamic(self,s3_bucket):
        cur_date = datetime.datetime.now().strftime('%Y_%m_%d')
        upload_cmd = "aws s3 cp dynamic_%s.zip %s/dynamic_%s.zip"%(cur_date,s3_bucket,cur_date)
        return subprocess.Popen(upload_cmd,shell=True)
    
    def download_dynamic(self,s3_bucket):
        cur_date = datetime.datetime.now().strftime('%Y_%m_%d')
        download_cmd = "aws s3 cp %s/dynamic_%s.zip ."%(s3_bucket,cur_date)
        return subprocess.Popen(download_cmd,shell=True)

    def unzip_dynamic(self,folder):
        cur_date = datetime.datetime.now().strftime('%Y_%m_%d')
        zip_cmd = "7z x dynamic_%s.zip -o%s -aoa"%(cur_date,folder)
        return subprocess.Popen(zip_cmd,shell=True) 

if __name__ == '__main__':
    t = StockDump()
    t.logger.info("start")
    #t.zip_dynamic('./data/dynamic')
    #t.upload_dynamic('s3://g1-build/tmp')
    t.download_dynamic('s3://g1-build/tmp')
    t.unzip_dynamic('./data')
    #t.dump_stock_dynamic(240,15)
    t.logger.info("end")


