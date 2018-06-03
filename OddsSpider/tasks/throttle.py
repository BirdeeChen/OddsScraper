import time
import random
from urllib.parse import urlparse

class Throttle:
    '''
    Add a delay between downloads to the same domain
    '''

    def __init__(self, delay=random.randrange(3)):
        # amount of delay between downloads for each domain
        self.delay = delay
        # timestamp of when a domain was last accessed
        self.domains = {}

    def wait(self, url):
        domain = urlparse(url).netloc
        last_accessed = self.domains.get(domain)
        if self.delay > 0 and last_accessed is not None:
            sleep_secs = self.delay - (time.time() - last_accessed)
            if sleep_secs > 0:
                # domain has been accessed recently (< delay), so need to sleep
                time.sleep(sleep_secs)
        # update the last accessed time
        self.domains[domain] = time.time()

if __name__ == '__main__':
    pass
