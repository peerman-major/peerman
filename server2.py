#!/usr/bin/env python
#
# Proof of Concept: UDP Hole Punching
# Two client connect to a server and get redirected to each other.
#
# This is the rendezvous server.
#
# Koen Bollen <meneer koenbollen nl>
# 2010 GPL
#

import socket
import struct
import sys
import time

def addr2bytes( addr ):
    """Convert an address pair to a hash."""
    host, port = addr
    try:
        host = socket.gethostbyname( host )
    except (socket.gaierror, socket.error):
        raise ValueError, "invalid host"
    try:
        port = int(port)
    except ValueError:
        raise ValueError, "invalid port"
    bytes  = socket.inet_aton( host )
    bytes += struct.pack( "H", port )
    return bytes

def main():
    port = 4653
    try:
        port = int(sys.argv[1])
    except (IndexError, ValueError):
        pass

    sockfd = socket.socket( socket.AF_INET, socket.SOCK_DGRAM )
    sockfd.bind( ("0.0.0.0", port) )
    print "listening on *:%d (udp)" % port
    dataqueue = {}
    poolqueue = {}
    while True:
        data, addr = sockfd.recvfrom(100)
        print "connection from %s:%d" % addr

        pool = data.strip()
        temp = pool.split("#")
        pool = temp[0]
        ## temp[1] and temp[2] contains localip, dataport 
        sockfd.sendto( "ok "+pool, addr )
        data, addr_ack = sockfd.recvfrom(40)
        ## received ok meassge from ack_port
        if data != "ok":
            continue
        ## saving ack_port in temp[3]
        temp.append(addr_ack[1])
        print "temp::",temp

        print "request received for pool:", pool

        try:
            a, b = poolqueue[pool], addr
            c = dataqueue[pool]
            print a,b
            if str(a[0])==str(b[0]):
                sockfd.sendto( str(c[1])+"#"+str(c[2])+'#'+str(c[3]), b )
                sockfd.sendto( str(temp[1])+"#"+str(temp[2])+'#'+str(temp[3]), a )
            else:
                sockfd.sendto( str(a[0])+"#"+str(a[1])+"#"+str(c[3]) , b )
                sockfd.sendto( str(b[0])+"#"+str(b[1])+"#"+str(temp[3]) , a )
            print "linked", pool
            #sockfd.sendto( "ssd", b )
            time.sleep(1)
            # try a connect to b
            sockfd.sendto( "connect", a )
            sockfd.sendto( "receive", b )

            is_connected,temp_addr= sockfd.recvfrom(50)

            if is_connected == "no":
                # try b connect to a
                sockfd.sendto( "connect", b )
                sockfd.sendto( "receive", a )
                is_connected,temp_addr= sockfd.recvfrom(50)
                if is_connected == "no":
                    sockfd.sendto( "turn", b )
                    sockfd.sendto( "turn", a )


            del poolqueue[pool]
            del dataqueue[pool]

        except KeyError:
            poolqueue[pool] = addr
            dataqueue[pool] = temp
        print "loop ends"


if __name__ == "__main__":
    main()

# vim: expandtab shiftwidth=4 softtabstop=4 textwidth=79:
