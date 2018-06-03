import random
from redis import StrictRedis
from configure import REDIS_PROXY_KEY
# REDIS_PROXY_KEY = 'Proxy'

class RedisProxy:
    def __init__(self, client = None, db=2, decode_responses = True):
        # if a client object is not passed then try
        # connecting to redis at the default localhost port
        self.client = StrictRedis(host = '127.0.0.1', port = 6379, db = db, decode_responses = decode_responses) if client is None else client
        # self.expires = expires

    def add_proxy(self, proxy):
        """
        add proxy to redis list
        :param proxy: new proxy or proxies
        """
        if isinstance(proxy, list):
            self.client.rpush(REDIS_PROXY_KEY, *proxy)
        else:
            self.client.rpush(REDIS_PROXY_KEY, proxy)

    def pop_proxy(self):
        '''Randomly pick a proxy from redis list.'''
        return random.choice(self.all_proxies())

    def all_proxies(self):
        return self.client.lrange(REDIS_PROXY_KEY, 0, -1)

    def flushredis(self):
        self.client.flushall()

if __name__ == '__main__':
    pass
    # cache = RedisProxy()
    # cache.add_proxy(1)
    # cache.add_proxy([3, 4, 5])
    # cache.add_proxy(['haha', 'heihei', 'karry'])
    # cache.add_proxy([6, 10, 35])
    # print (cache.all_proxies())
    # print (cache.pop_proxy())
            
