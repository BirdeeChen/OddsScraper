from db import RedisProxy
proxypool = RedisProxy()
from configure import USER_AGENT
# USER_AGENT = 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/66.0.3359.181 Safari/537.36'
headers = {'user-agent': USER_AGENT}
# from tasks.cndownloader_firefox import Downloader
# import time
# proxypool.flushredis()
# from proxy import proxycrawler
# proxycrawler.run()
# from proxy import proxycrawler
# proxycrawler.run()
import requests
# # from bs4 import BeautifulSoup
proxyapi = 'http://ip.11jsq.com/index.php/api/entry?method=proxyServer.generate_api_url&packid=1&fa=0&fetch_key=&qty=1&time=1&pro=&city=&port=1&format=txt&ss=1&css=&dt=1'
# # proxytest = proxypool.pop_proxy()
# # print (proxytest)
# # proxytest = {proxytest.split('://')[0] : proxytest}
# # print (proxytest)

# print(proxy_new)
# # print (proxies)
# proxytest = ['http://{}'.format(proxy) for proxy in proxies]
# print (proxytest)
proxytest = {'http' : proxypool.pop_proxy()}
# print (proxytest)
# url = 'https://whatismyipaddress.com/'
url = 'https://api.ipify.org/'

print ('Downloading with wrong proxy.', proxytest)
resp = requests.get(url, proxies = proxytest)
# resp = requests.get(url)
print ('wrong proxy response status.', resp.status_code)
print (resp.text)

proxy_new = {'http' : 'http://{}'.format(requests.get(proxyapi).text)}
print ('Downloading with fresh proxy.', proxy_new)
resp_new = requests.get(url, proxies = proxy_new, headers = headers)
print ('Fresh proxy response status.', resp_new.status_code)
print (resp_new.text)

# bsObj = BeautifulSoup(resp.text, 'html.parser')

# print (bsObj.find('div', id = 'ipv4').string)
# downloader = Downloader()
# print ('Downloading ', url, 'with proxy ', downloader.proxy)
# downloader.driver.get(url)
# # time.sleep(5)
# # print (downloader.driver.find_element_by_id('ipv4').text)
# print (downloader.driver.find_element_by_tag_name('pre').text)
