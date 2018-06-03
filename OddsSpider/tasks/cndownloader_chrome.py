#This script is not working due to some unknown reason, when setting try downloading with proxies
import time
import random
from db import RedisProxy
from .throttle import Throttle
from configure import USER_AGENT
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import WebDriverException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver import Proxy
from selenium.webdriver import DesiredCapabilities
proxypool = RedisProxy()

class Downloader:
    """ Downloader class to requests for downloading pages.
        initial parameters:
        kwargs:
            delay (int) : time to wait upon the same domain, default to 2 sec
            proxy (dict) : proxy to be used, default to None
    """
    #class variables
    PROXY = proxypool.pop_proxy().split('://')[-1]
    # settings = {'httpProxy' : proxypool.pop_proxy().split('://')[-1],
    #             'httpsProxy' : proxypool.pop_proxy().split('://')[-1],
    #             'sslProxy' : proxypool.pop_proxy().split('://')[-1]}
    # PROXY = settings['httpProxy']
    # proxy = Proxy(settings)
    # cap = DesiredCapabilities.CHROME.copy()
    # cap['platform'] = 'WINDOWS'
    # cap['version'] = '10'
    # proxy.add_to_capabilities(cap)
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--disable-gpu')
    chrome_options.add_argument('--ignore-certificate-errors')
    chrome_options.add_argument('--user-agent={}'.format(USER_AGENT))
    chrome_options.add_argument('--proxy-server=%s' % PROXY)
    driver = webdriver.Chrome(chrome_options=chrome_options)

    def __init__(self, delay=2):
        # instance variables
        self.throttle = Throttle(delay)

    def __call__(self, url):
        """ Call the downloader class, which will return download HTML
            args:
                url (str): url to download
            kwargs:
                callback (int): function to be called on parsing HTML, default to None
        """
        self.throttle.wait(url)
        print('Downloading:', url, 'with proxy {}'.format(self.PROXY))
        # print ('Downloading:', url)
        try:
            self.driver.get(url)
            # time.sleep(5)
            # print(self.driver.title)
            # 增加从conf获取配置参数的代码
            WebDriverWait(self.driver, 10).until(EC.presence_of_all_elements_located((By.CLASS_NAME, 'listTr')))
            # result = self.driver.find_element_by_id('mainTbl').get_attribute('outerHTML')
            # print(self.driver.page_source)
            header = self.driver.find_element_by_id('headerTr').get_attribute('outerHTML')
            events = [element.get_attribute('outerHTML') for element in self.driver.find_elements_by_class_name('listTr')]
            self.driver.quit()
            return header, events
            
        except WebDriverException as e:
            print('Downloading Error ->', e)

if __name__ == '__main__':
    pass
