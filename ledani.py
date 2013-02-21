'''
The polling part of the project
'''

from argparse import ArgumentParser
from ConfigParser import ConfigParser

import envoy
import threading
from Queue import Queue
from RPi import GPIO

from pprint import pprint

################################################################################
# networking checks

def check_host(host, host_queue):
    r = envoy.run('ping -c 1 {0}'.format(host))
    if r.status_code == 0:
        host_queue.put(host)

def find_hosts(ip_range):
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
    return sorted(hosts)

def find_macs(hosts):
    '''
    Given a list of hosts, find their MAC addresses via ARP
    '''
    macs = []
    for h in hosts:
        r = envoy.run('arp {0}'.format(h))
        if r.status_code == 0:
            # ugh parsing CLI output
            lines = r.std_out.split('\n')[1:]
            # ugh case-handling output formatting
            if lines and len(lines[0]) > 2:
                mac = lines[0].split()[2]
                macs.append(mac)
    return sorted(set(macs))

################################################################################
# LED fiddling

def mac_to_pin(macs, config):
    '''
    Map from recognized MAC addresses to which pins to flip, using a
    text config
    '''
    pins = {}
    for mac,pin in config.items('MAC'):
        pins[pin] = bool(mac in macs)
    return pins

def effect_pins(pins):
    '''
    Given a mapping of pins to states {pin: state}, set the pins to
    the right state
    '''
    GPIO.setmode(GPIO.BOARD)
    for pin,state in pins.iteritems():
        GPIO.setup(pin, GPIO.OUT)
        if state:
            GPIO.output(pin, GPIO.HIGH)
        else:
            GPIO.output(pin, GPIO.LOW)

################################################################################
# main

if __name__ == '__main__':
    parser = ArgumentParser(description=('A utility to flip raspberry pi GPIO '
                                         'outputs based on the presence of MAC '
                                         'addresses on a network.'))
    parser.add_argument('config', type='str', default='ledani.conf',
                        help=('Path to the configuration file containing the '
                              'MAC address to pin mapping, and IP ranges to '
                              'scan.'))
    args = parser.parse_args()

    config = ConfigParser()
    config.readfp(open(args.config))
    ips = config.get('IP', 'address-range')

    hosts = find_hosts(ips)
    macs = find_macs(hosts)
    pins = mac_to_pin(macs, config)
    effect_pins(pins)
