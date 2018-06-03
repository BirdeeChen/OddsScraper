import time
import random
from db import RedisProxy
# from .throttle import Throttle
from proxy import proxycrawler
from selenium import webdriver
from selenium.webdriver import FirefoxOptions
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import WebDriverException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.proxy import Proxy, ProxyType

from configure import USER_AGENT

proxypool = RedisProxy()

class Downloader:
    """ Downloader class to requests for downloading pages.
        initial parameters:
        kwargs:
            delay (int) : time to wait upon the same domain, default to 2 sec
            proxy (dict) : proxy to be used, default to None
    """
    #class variables
    proxy = proxypool.pop_proxy()
    proxy_obj = Proxy({'proxyType' : ProxyType.MANUAL, 
                   'httpProxy': proxy, 
                   'httpsProxy' : proxy,
                   'sslProxy' : proxy})
    firefox_options = FirefoxOptions()
    firefox_options.set_headless(headless = True)
    driver = webdriver.Firefox(firefox_options = firefox_options, proxy = proxy_obj)

    def __call__(self, url):
        """ Call the downloader class, which will return download HTML
            args:
                url (str): url to download
            kwargs:
                callback (int): function to be called on parsing HTML, default to None
        """
        # self.throttle.wait(url)
        print('Downloading:', url, 'with proxy {}'.format(self.proxy))
        # print ('Downloading:', url)
        try:
            self.driver.get(url)
            # 增加从conf获取配置参数的代码
            WebDriverWait(self.driver, 10).until(EC.presence_of_all_elements_located((By.CLASS_NAME, 'listTr')))
            header = self.driver.find_element_by_id('headerTr').get_attribute('outerHTML')
            events = [element.get_attribute('outerHTML') for element in self.driver.find_elements_by_class_name('listTr')]
            self.driver.quit()
            return header, events
        except WebDriverException as e:
            print('Downloading Error ->', e)

if __name__ == '__main__':
    pass
