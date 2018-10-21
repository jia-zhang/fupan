import requests
import re
import time
import os
import json
import random

class StockQuery():
    def __init__(self):
        #self.stock_list_url = "http://quote.eastmoney.com/stocklist.html"
        pass
    
    def get_stock_list(self):
        resp = requests.get("http://quote.eastmoney.com/stocklist.html")
        resp.encoding = 'gb2312'
        s = r'<li><a target="_blank" href="http://quote.eastmoney.com/(.*?).html">'
        pat = re.compile(s)
        codes = pat.findall(resp.text)
        return codes

    def save_stock_list(self,file_name):
        ret = []
        all_stocks = self.get_stock_list()
        for n in all_stocks:
            if n.startswith('sz00') or n.startswith('sh60') or n.startswith('sz300'):
                ret.append(n)
        with open(file_name,'w') as f:
            f.write(",".join(ret))
    
    def get_stock_list_from_file(self,file_name):
        with open(file_name,'r') as f:
            output = f.read()
        return output.split(',')
    
    def get_stock_detail(self,stock_id,time_range,count):
        #headers={'User-Agent':'Mozilla/5.0 (Windows NT 6.3; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/44.0.2403.157 Safari/537.36'}
        detail_url = ("http://money.finance.sina.com.cn/quotes_service/api/json_v2.php/CN_MarketData.getKLineData?"
                    "symbol=%s&scale=%s&ma=no&datalen=%s"
        )%(stock_id,time_range,count)
        resp = requests.get(detail_url)
        return resp.text.replace('day','"day"').replace('open','"open"').replace('low','"low"').\
        replace('high','"high"').replace('close','"close"').replace('volume','"volume"')
    
    def get_stock_basic(self,stock_id,item):
        #resp = requests.get("http://finance.sina.com.cn/realstock/company/%s/nc.shtml"%(stock_id))
        headers={'User-Agent':'Mozilla/5.0 (Windows NT 6.3; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/44.0.2403.157 Safari/537.36'}
        resp = requests.get("https://xueqiu.com/S/%s"%(stock_id),headers=headers)
        resp.encoding = 'gb2312'
        #s = r'var currcapital = (.*?);'
        s = r'"float_shares":(\d*?),'
        pat = re.compile(s)
        codes = pat.findall(resp.text)
        return codes[0]

    def get_last_trading_date(self):
        #headers={'User-Agent':'Mozilla/5.0 (Windows NT 6.3; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/44.0.2403.157 Safari/537.36'}
        detail_url = "http://money.finance.sina.com.cn/quotes_service/api/json_v2.php/CN_MarketData.getKLineData?symbol=sh000001&scale=240&ma=no&datalen=5"
        resp = requests.get(detail_url)
        return eval(resp.text.replace('day','"day"').replace('open','"open"').replace('low','"low"').\
        replace('high','"high"').replace('close','"close"').replace('volume','"volume"'))[-1]['day']
    
    def dump_stock_dynamic(self):
        '''
        Get stock dynamic info, 10 days open,high,low,close,volume
        '''
        s_list = self.get_stock_list_from_file('stocks.csv')
        i=0
        for s in s_list:
            print("Dumping stock dynamic %s..."%(s))
            if (os.path.exists("./data/%s.json"%(s))):
                print("%s already exists, skip"%(s))
                continue
            stock_detail = self.get_stock_detail(s,240,10)
            i=i+1
            with open("./data/%s.json"%(s),'w') as f:
                f.write(stock_detail)
            if (i%10==0):
                time.sleep(1)
    
    def dump_stock_static(self):
        '''
        Get stock static info, eg: name, float_shares, market_capital to one file.
        '''
        s_list = self.get_stock_list_from_file('d:\\jia\\jiazzz\\fupan\\lib\\stocks.csv')
        headers={'User-Agent':'Mozilla/5.0 (Windows NT 6.3; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/44.0.2403.157 Safari/537.36'}
        i=0
        f = open("stock_static.json",'w')
        #f.write('{')
        master_dict = {}
        for s in s_list:
            print("Dumping stock static %s..."%(s))
            resp = requests.get("https://xueqiu.com/S/%s"%(s),headers=headers)
            if (resp.status_code==404):
                print("Get code 404 on stock %s"%(s))
                continue
            resp.encoding = 'utf-8'
            float_shares = re.compile(r'"float_shares":(.*?),').findall(resp.text)[0]
            stock_name = re.compile(r'"name":(.*?),').findall(resp.text)[0]      
            market_capital = re.compile(r'"market_capital":(.*?),').findall(resp.text)[0]             
            stock_dict = {}
            stock_dict['float_shares'] = str(float_shares)  
            stock_dict['stock_name'] = str(stock_name)
            stock_dict['market_capital'] = str(market_capital)
            master_dict[s] = stock_dict
            #i = i+1
            #if i==3:
            #    break
            time.sleep(random.randint(1,5))
        f.write(json.dumps(master_dict))
        #f.write('}')
        f.close()

    

if __name__ == '__main__':
    t = StockQuery()
    t.dump_stock_static()
    #t.save_stock_list("stocks.csv")
    #print(t.get_last_trading_date())
    #print(t.get_stock_detail('sz000007',240,10))

