import requests

'''
#Change num=10 to your desired value
url = 'http://vip.stock.finance.sina.com.cn/quotes_service/api/json_v2.php/Market_Center.getHQNodeData?page=1&\
num=100&sort=changepercent&asc=0&node=hs_a&symbol=&_s_r_a=init' 

r = requests.get(url)
o = r.text
o1 = o.replace('symbol','"symbol"').replace('code','"code"').replace('name','"name"').replace('trade','"trade"')\
.replace('pricechange','"pricechange"').replace('changepercent','"changepercent"').replace('buy','"buy"').\
replace('sell','"sell"').replace('settlement','"settlement"').replace('open','"open"').replace('high','"high"').\
replace('low','"low"').replace('volume','"volume"').replace('amount','"amount"').replace('ticktime','"ticktime"').\
replace('per:','"per":').replace('pb','"pb"').replace('mktcap','"mktcap"').replace('nmc','"nmc"').\
replace('turnoverratio','"turnoverratio"').replace('pb:','"pb":')
o2 = eval(o1)
'''

def get_top_n(n):
    url = "http://vip.stock.finance.sina.com.cn/quotes_service/api/json_v2.php/Market_Center.getHQNodeData?page=1&\
num=%s&sort=changepercent&asc=0&node=hs_a&symbol=&_s_r_a=init"%(n)
    r = requests.get(url)
    ret = translate_sina(r.text)
    return eval(ret)

def translate_sina(input_str):
    return input_str.replace('symbol','"symbol"').replace('code','"code"').replace('name','"name"').replace('trade','"trade"')\
.replace('pricechange','"pricechange"').replace('changepercent','"changepercent"').replace('buy','"buy"').\
replace('sell','"sell"').replace('settlement','"settlement"').replace('open','"open"').replace('high','"high"').\
replace('low','"low"').replace('volume','"volume"').replace('amount','"amount"').replace('ticktime','"ticktime"').\
replace('per:','"per":').replace('pb','"pb"').replace('mktcap','"mktcap"').replace('nmc','"nmc"').\
replace('turnoverratio','"turnoverratio"').replace('pb:','"pb":')

o2 = get_top_n(10)
for s in o2:
    print("%s\t%s\t%s\t%s"%(s['code'],s['name'],s['changepercent'],s['turnoverratio']))

#get high change
#get high volume
#dump trans data
#analyze

