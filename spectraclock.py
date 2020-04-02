#!/usr/bin/env python3

import argparse
import serial
import sched
import time
import re

def parseArgs():
    p = argparse.ArgumentParser(description='Control an attached Symmetricom clock.')
    p.add_argument('dev', help='Serial device (i.e. /dev/ttyAMA0)')
    p.add_argument('--debug', action='store_true', help='Enable debug output.')
    p.add_argument('--utc', action='store_true', help='Output UTC time instead of local time.')
    p.add_argument('--unsync', action='store_true', help='Send unsyncronized flag in output.')
    return p.parse_args()

def formatTime(t, ss = " "):    
    # Return binary encoded time in Symmetricom Format 1
    # t = Time to return formatted, in struct_time format
    # ss = Sync status; " " (space) indicates good, ? and * indicate bad
    dn = time.strftime("%a", t).upper()
    d = re.sub("^0", " ", str(time.strftime("%d", t)))
    m = time.strftime("%b", t).upper()
    y = time.strftime("%y", t)
    hms = time.strftime("%H:%M:%S", t)
    string = "\r\n" + ss + " " + dn + " " + d + m + y + " " + hms + "\r\n"
    return str.encode(string)

def sendTime(ser, args):
    if args.unsync:
        ss = "*"
    else:
        ss = " "
    if args.utc:
        t = time.gmtime()
    else:
        #t = time.strptime("10 Apr 20", "%d %b %y")
        t = time.localtime()
    msg = formatTime(t, ss)
    ser.write(msg)
    if args.debug:
        print(msg)

def main(args = parseArgs()):
    ser = serial.Serial(args.dev, 9600)
    s = sched.scheduler(time.time, time.sleep)
    while True:
        s.enterabs(int(time.time()) + 1, 1, sendTime, 
                kwargs={'ser': ser, 'args': args})
        s.run()

if __name__ == "__main__":
    main()
