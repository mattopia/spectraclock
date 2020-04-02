#!/usr/bin/env python3

import argparse
import serial
import sched
import time
import re

def parseArgs():
    p = argparse.ArgumentParser(description='Synchronize an attached Spectracom clock.')
    p.add_argument('dev', help='Serial device (i.e. /dev/ttyAMA0)')
    p.add_argument('--debug', action='store_true', help='Enable debug output.')
    p.add_argument('--utc', action='store_true', help='Output UTC time instead of local time.')
    p.add_argument('--unsync', action='store_true', help='Send unsyncronized flag in output.')
    return p.parse_args()

def formatTime(t, ss = " "):    
    # Return binary encoded time in Spectracom Format 1
    # t = Time to return formatted, in struct_time format
    # ss = Sync status; " " (space) indicates good, ? and * indicate bad
    day = time.strftime("%a", t)
    dmy = re.sub("^0", " ", str(time.strftime("%d%b%y", t)))
    hms = time.strftime("%H:%M:%S", t)
    return str.encode(f"\r\n{ss} {day} {dmy} {hms}\r\n".upper())

def sendTime(ser, unsync = False, utc = False, debug = False):
    ss = "*" if unsync else " "
    t = time.gmtime() if utc else time.localtime()
    msg = formatTime(t, ss)
    ser.write(msg)
    if debug:
        print(msg)

def main(args = parseArgs()):
    try:
        ser = serial.Serial(args.dev, 9600)
        s = sched.scheduler(time.time, time.sleep)
        while True:
            s.enterabs(int(time.time()) + 1, 1, sendTime, 
                kwargs={'ser': ser, 'unsync': args.unsync, 'utc': args.utc, 'debug': args.debug})
            s.run()
    except KeyboardInterrupt:
        print("Exiting...")
        ser.close

if __name__ == "__main__":
    main()
