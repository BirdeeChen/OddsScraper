import re
import requests
import time
from db import RedisProxy
from bs4 import BeautifulSoup
from configure import USER_AGENT
# USER_AGENT = 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/66.0.3359.181 Safari/537.36'
redis_proxy = RedisProxy()
headers = {'user-agent' : USER_AGENT}
all_func = []

def collector(func):
    '''Decorator for collecting crawling function.'''
    all_func.append(func)
    return func

class proxyCrawler:

    @staticmethod
    def run():
        for func in all_func:
            for proxy in func():
                redis_proxy.add_proxy(proxy)

    @staticmethod
    # @collector
    def proxy_66ip():
        '''66ip代理:http://www.66ip.cn'''
        url = 'http://www.66ip.cn/nmtq.php?getnum=100&isp=0&anonymoustype=3&start=&ports=&export=&ipaddress=&area=1&proxytype={}&api=66ip'
        pattern = "\\d+\\.\\d+.\\d+\\.\\d+:\\d+"
        items = [(0, "HTTP://{}"), (1, "HTTPS://{}")]
        for item in items:
            proxy_type, host = item
            html = requests.get(url.format(proxy_type), headers = headers).text
            if html:
                for proxy in re.findall(pattern, html):
                    yield host.format(proxy)

    @staticmethod
    # @collector
    def proxy_xici():
        '''西刺代理:http://www.xicidaili.com/'''
        url = "http://www.xicidaili.com/nn/{}"
        items = []
        for page in range(1, 11):
            items.append((page, "{}://{}:{}"))

        for item in items:
            page, host = item
            html = requests.get(url.format(page), headers = headers).text
            if html:
                bsObj = BeautifulSoup(html, 'html.parser')
                for proxy in bsObj.find('table', id = 'ip_list').find_all('tr')[1:]:
                    proxy_type = proxy.contents[11].string
                    ip = proxy.contents[3].string
                    port = proxy.contents[5].string
                    if proxy_type in ['HTTP', 'HTTPS'] and ip and port:
                        yield host.format(proxy_type, ip, port)

    @staticmethod
    @collector
    def proxy_zhilian():
        '''直联代理：http://www.jinglingdaili.com/'''
        url = 'http://ip.11jsq.com/index.php/api/entry?method=proxyServer.generate_api_url&packid=1&fa=0&fetch_key=&qty=9&time=1&pro=&city=&port=1&format=txt&ss=1&css=&dt=1'
        proxies = requests.get(url).text.split('\r\n')
        for proxy in proxies:
            yield 'http://{}'.format(proxy)

proxycrawler = proxyCrawler()

if __name__ == '__main__':
    pass
