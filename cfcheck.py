import datetime
import io
import random
import time

from enum import Enum
from sigtools.modifiers import kwoargs

import clize
import pycurl
import stem.process

SOCKS_PORT = 7000
RATE = 15


class Status(Enum):
    other = 1
    cloudflare_active = 2
    captcha = 3
    tor_timeout = 4


def query(url):
    ''' Uses pycurl to fetch a site using the proxy on the SOCKS_PORT.  '''
    output = io.BytesIO()
    query = pycurl.Curl()
    query.setopt(pycurl.URL, url)
    query.setopt(pycurl.PROXY, 'localhost')
    query.setopt(pycurl.PROXYPORT, SOCKS_PORT)
    query.setopt(pycurl.PROXYTYPE, pycurl.PROXYTYPE_SOCKS5_HOSTNAME)
    query.setopt(pycurl.WRITEFUNCTION, output.write)

    try:
        query.perform()
        return output.getvalue()
    except pycurl.error as exc:
        raise RuntimeError('Unable to reach {} {}'.format(url, exc))


def check_page(url, exit_ip):
    def site_status(page_body):
        body_text = page_body.decode('utf-8')

        # Rough, could do with real heuristics
        if 'CAPTCHA' in body_text:
            return Status.captcha
        elif 'CloudFlare' in body_text:
            return Status.cloudflare_active
        else:
            return Status.other

    config = {
        'SocksPort': str(SOCKS_PORT),
        'ExitNodes': exit_ip,
    }

    try:
        tor_process = stem.process.launch_tor_with_config(config=config)
    except OSError as e:
        if 'timeout' in str(e):
            # Exit might be dead
            tor_process.kill()
            return Status.tor_timeout

    status = site_status(query(url))
    tor_process.kill()
    return status


@kwoargs('randomize_ips', 'sample_size', 'rate')
def main(domain, exits, rate=15, randomize_ips=False, sample_size=100):
    timestamp = datetime.datetime.now().strftime('%c').replace(' ', '-')
    outfile = 'results/{}_{}'.format(domain, timestamp)

    with open(exits, 'r') as f:
        exit_ips = [l.strip() for l in f.readlines()]
        if randomize_ips:
            random.shuffle(exit_ips)

    with open(outfile, 'w') as f:
        for exit_ip in exit_ips[:sample_size]:
            for protocol in ('http', ):
                url = '{}://{}'.format(protocol, domain)
                status = check_page(url, exit_ip)
                line = '{}, {}'.format(exit_ip, status.name)
                print(line)
                time.sleep(rate)

if __name__ == '__main__':
    clize.run(main)
