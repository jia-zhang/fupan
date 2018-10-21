import json

class StockTag():
    def __init__(self):
        pass
    
    def add_propery(self,stock_id,property_dict):
        file_name = "./data/%s.static.json"%(stock_id)
        f = open(file_name,'r',encoding='utf-8')
        info = json.load(f)
        f.close()
        for key in property_dict.keys():
            info[stock_id][key] = property_dict[key]
        print(info)
        with open(file_name,'w') as f:
            f.write(json.dumps(info))
    
    def remove_property(self,stock_id,property_key):
        file_name = "./data/%s.static.json"%(stock_id)
        f = open(file_name,'r',encoding='utf-8')
        info = json.load(f)
        f.close()
        info[stock_id].pop(property_key)
        print(info)
        with open(file_name,'w') as f:
            f.write(json.dumps(info))


    def add_tag(self,stock_id,new_tag):
        file_name = "./data/%s.static.json"%(stock_id)
        f = open(file_name,'r',encoding='utf-8')
        info = json.load(f)
        f.close()
        tags = []
        if 'tag' in info[stock_id]:
            tags = info[stock_id]['tag'].split(',')
        if type(new_tag)==str:
            tags.append(new_tag)
        else:
            tags.extend(new_tag) #only support add new list now, need to add support str
        info[stock_id]['tag'] = ','.join(tags)
        with open(file_name,'w') as f:
            f.write(json.dumps(info))
    
    def get_tag(self,stock_id):
        file_name = "./data/%s.static.json"%(stock_id)
        f = open(file_name,'r',encoding='utf-8')
        info = json.load(f)
        f.close()
        tags = []
        if 'tag' in info[stock_id]:
            return info[stock_id]['tag']
        else:
            return "no tag!"

if __name__ == '__main__':
    t = StockTag()
    #t.add_tag('sz000002', '稀土')
    #print(t.get_tag('sz000002'))
    #t.add_propery('sh600000',{"tag1":{"ddd":"ccc"}})
    t.remove_property('sh600000','tag1')
