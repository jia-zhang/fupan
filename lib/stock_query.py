import requests
import re

class StockQuery():
    def __init__(self):
        self.stock_list_url = "http://quote.eastmoney.com/stocklist.html"
        pass
    
    def get_stock_list(self):
        resp = requests.get(self.stock_list_url)
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
        detail_url = ("http://money.finance.sina.com.cn/quotes_service/api/json_v2.php/CN_MarketData.getKLineData?"
                    "symbol=%s&scale=%s&ma=no&datalen=%s"
        )%(stock_id,time_range,count)
        resp = requests.get(detail_url)
        return resp.text.replace('day','"day"').replace('open','"open"').replace('low','"low"').\
        replace('high','"high"').replace('close','"close"').replace('volume','"volume"')
    
    def get_last_trading_date(self):
        detail_url = "http://money.finance.sina.com.cn/quotes_service/api/json_v2.php/CN_MarketData.getKLineData?symbol=sh000001&scale=240&ma=no&datalen=5"
        resp = requests.get(detail_url)
        return eval(resp.text.replace('day','"day"').replace('open','"open"').replace('low','"low"').\
        replace('high','"high"').replace('close','"close"').replace('volume','"volume"'))[-1]['day']

    

if __name__ == '__main__':
    t = StockQuery()
    #t.save_stock_list("stocks.csv")
    print(t.get_last_trading_date())

