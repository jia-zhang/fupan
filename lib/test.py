f = open('stocks.csv','r')
all_stock = f.read().split(',')

g = open('incomplete.csv','r')
stock_404 = g.read().split(',')

h = open('valid_stock.csv','w')

try:
    for s in stock_404:
        all_stock.remove(s)
except:
    print(s)

#print(all_stock)
h.write(','.join(all_stock))

f.close()
g.close()
h.close()
