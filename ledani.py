'''
The polling part of the project
'''

from argparse import ArgumentParser
from ConfigParser import ConfigParser

import envoy
import threading
from Queue import Queue
#from RPi import GPIO

import struct
import socket

from pprint import pprint

################################################################################
# networking checks

def check_host(host, host_queue):
    r = envoy.run('ping -c 1 {0}'.format(host))
    if r.status_code == 0:
        host_queue.put(host)

def get_ip_addr():
    '''
    Get the current ip address and subnet mask
    '''
    r = envoy.run('ip addr')
    lines = r.std_out.split('\n')
    inets = [l.strip().split() for l in lines if l.strip().startswith('inet ')]
    inets = [i for i in inets if not i[1].startswith('127')]
    if len(inets) == 1:
        return inets[0][1]
    elif inets:
        raise ValueError('Too many suitable IP addresses found')
    else:
        raise ValueError('No suitable IP address found')
    
def generate_ips(ip_range):
    '''
    Given an ip range of the format X.X.X.X/Y, generate a series of IP
    addresses in that range
    '''
    addr, mask_size = ip_range.split('/')
    mask_size = int(mask_size)
    # convert the address stuff to numbers
    mask = (2 << (mask_size-1)) - 1
    start = struct.unpack('I', socket.inet_aton(addr))[0]
    start = start & mask
    # to do addition, need to flip the octets around
    base = struct.unpack('I', struct.pack('I', start)[::-1])[0]
    for i in range((2 << (32 - mask_size - 1)) - 1):
        yield socket.inet_ntoa(struct.pack('I', base + i)[::-1])

def find_hosts():
    '''
    Find hosts by pinging them in parallel
    '''
    hosts = []
    threads = []
    host_queue = Queue()
    for h in generate_ips(get_ip_addr()):
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
    for pin,mac in config.items('MAC'):
        pins[int(pin)] = bool(mac in macs)
    return pins

def effect_pins(pins):
    '''
    Given a mapping of pins to states {pin: state}, set the pins to
    the right state
    '''
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
    parser.add_argument('--conf', dest='config', type=str, default='ledani.conf',
                        help=('Path to the configuration file containing the '
                              'MAC address to pin mapping, and IP ranges to '
                              'scan.'))
    args = parser.parse_args()

    config = ConfigParser()
    config.readfp(open(args.config))

    status_pin = config.get('STATUS', 'pin')

    GPIO.setmode(GPIO.BOARD)
    try:
        hosts = find_hosts()
        macs = find_macs(hosts)
        pins = mac_to_pin(macs, config)
        effect_pins(pins)
    except:
        # if everything goes wrong, set the status pin to off
        GPIO.setup(status_pin, GPIO.OUT)
        GPIO.output(status_pin, GPIO.LOW)
    else:
        GPIO.setup(status_pin, GPIO.OUT)
        GPIO.output(status_pin, GPIO.HIGH)
