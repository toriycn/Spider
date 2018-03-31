import requests
import json
from Spider.middlewares import RandomIPMiddleware

# 先运行IPProxyPool，调用接口获取ip
#
# 接口参数如下
# types	int	0: 高匿,1:匿名,2 透明
# protocol	int	0: http, 1 https, 2 http/https
# count	int	数量
# country	str	取值为 国内, 国外
# area	str	地区
#
# param = {'type':'1','country':'国内','count':'5'}
# ips = requests.get('http://localhost:8000',params=param)

# param = {'type':'1','country':'国内'}
# ipsinfojson = requests.get('http://localhost:8000',params=param)
# ipsinfo = json.loads(ipsinfojson.text)
# ips = []
# for ipinfo in ipsinfo:
#     ip = '%s:%s' % (ipinfo[0],ipinfo[1])
#     ips.append(ip)
# print(len(ips))

# middleware = RandomIPMiddleware()
# for i in range(17):
#     print(middleware.getrandomip())