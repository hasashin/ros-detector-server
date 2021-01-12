#!/usr/bin/env python3

import rospy
import socket,struct
import netifaces as ni


def makeMask(n):
    "return a mask of n bits as a long integer"
    return (int(2)<<n-1) - 1

def dottedQuadToNum(ip):
    "convert decimal dotted quad string to long integer"
    return struct.unpack('I',socket.inet_aton(ip))[0]

def networkMask(ip,bits):
    "Convert a network address to a long integer" 
    return dottedQuadToNum(ip) & makeMask(bits)

def addressInNetwork(ip,net):
   "Is an address in a network"
   return ip & net == net

def dotted_mask_to_num(mask):
    sections = mask.split('.')
    text = ''
    for section in sections:
        text = text + "{0:#b}".format(int(section))
    return text.count('1')

def net_addres(ip, mask):
    ip_sections = ip.split('.')
    mask_sections = mask.split('.')
    net_addr = []
    for i in range(len(ip_sections)):
        net_addr.append(str(int(ip_sections[i]) & int(mask_sections[i])))
    return '.'.join(net_addr)

def addr_to_bytes(addr):
    addr_sections = addr.split('.')
    byts = bytes(0)
    for addr_section in addr_sections:
        byts = byts + int(addr_section).to_bytes(1,'big')
    return byts

print('ROS Detector Server is starting...')

rosbridge_port = 9090

interface_addresses = []

for interface in ni.interfaces():
    interface_addresses.append(ni.ifaddresses(interface))

listen_socket=socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
listen_socket.bind(('',21337))

print('ROS Detector Server started')
print('Local IP address: ', listen_socket.getsockname())

while True:
    try:
        m=listen_socket.recvfrom(1024)
        print('Got request from client: {}'.format(m[1][0]))
        if m[0].decode('ASCII') == 'ROS':
            ip, port = m[1]
            for address in interface_addresses:
                clinent_address = dottedQuadToNum(ip)
                network = networkMask(net_addres(address[2][0]['addr'], address[2][0]['netmask']),dotted_mask_to_num(address[2][0]['netmask']))
                if addressInNetwork(clinent_address,network):
                    listen_socket.sendto('ACK'.encode('ASCII')+addr_to_bytes(address[2][0]['addr'])+rosbridge_port.to_bytes(2,'big'),m[1])
    except KeyboardInterrupt:
        break

listen_socket.close()