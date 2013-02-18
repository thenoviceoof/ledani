'''
The polling part of the project
'''

from RPi import GPIO

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
    return sorted(macs)

################################################################################
# LED fiddling

def mac_to_pin(macs):
    '''
    Map from recognized MAC addresses to which pins to flip, using a
    text config
    '''
    # get config
    # go through each person's stored MAC, see if it's in the given list
    # if so, turn that pin on

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

hosts = find_hosts()
print hosts
macs = find_macs(hosts)
print macs
