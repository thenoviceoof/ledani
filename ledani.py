'''
The polling part of the project
'''

#from RPi import GPIO

import envoy
import threading
from Queue import Queue

from pprint import pprint

################################################################################
# networking checks

def check_host(host, host_queue):
    r = envoy.run('ping -c 1 {0}'.format(host))
    if r.status_code == 0:
        host_queue.put(host)

def find_hosts():
    '''
    Find hosts by pinging them in parallel
    '''
    hosts = []
    threads = []
    host_queue = Queue()
    for i in range(255):
        h = '192.168.1.{0}'.format(i+1)
        thread = threading.Thread(target=check_host, args=(h, host_queue))
        thread.start()
        threads.append(thread)
    for thread in threads:
        thread.join()
    while not host_queue.empty():
        host = host_queue.get()
        hosts.append(host)
    return hosts

def find_macs(hosts):
    '''
    Given a host, find it's MAC address via ARP
    '''
    macs = []
    for h in hosts:
        r = envoy.run('arp {0}'.format(h))
        if r.status_code == 0:
            lines = r.std_out.split('\n')[1:]
            if lines and len(lines[0]) > 2:
                mac = lines[0].split()[2]
                macs.append(mac)
    return macs

################################################################################
# LED fiddling

################################################################################
# main

hosts = find_hosts()
print hosts
macs = find_macs(hosts)
print macs
