#!/usr/bin/env python3

import subprocess
import argparse
import serial
import sched
import time
import re

def parseArgs():
    p = argparse.ArgumentParser(description='Synchronize attached Spectracom RS-485 clock(s).')
    p.add_argument('dev', help='Serial device (i.e. /dev/ttyAMA0)')
    p.add_argument('--debug', action='store_true', help='Enable debug output.')
    p.add_argument('--utc', action='store_true', help='Output UTC time instead of local time.')
    return p.parse_args()

def checkNtpSync():
    p = subprocess.Popen(['chronyc', '-c', 'tracking'], stdout=subprocess.PIPE)
    try:
        output, errors = p.communicate(timeout = 0.1)
    except subprocess.TimeoutExpired:
        print("NTP Check - Timeout Exceeded")
        p.kill()
        return False
    status = output.decode().split(",")[0]
    offset = float(output.decode().split(",")[4])
    if offset > 0.1 or offset < -0.1:
        return False
    if status != "00000000" and p.returncode == 0 and errors == None:
        return True
    else:
        return False

def formatTime(t, ss = " "):    
    # Return binary encoded time in Spectracom Format 1
    # t = Time to return formatted, in struct_time format
    # ss = Sync status; " " (space) indicates good, ? and * indicate bad
    day = time.strftime("%a", t)
    dmy = re.sub("^0", " ", str(time.strftime("%d%b%y", t)))
    hms = time.strftime("%H:%M:%S", t)
    return str.encode(f"\r\n{ss} {day} {dmy} {hms}\r\n".upper())

def sendTime(ser, sync = True, utc = False, debug = False):
    ss = " " if sync else "*"
    t = time.gmtime() if utc else time.localtime()
    msg = formatTime(t, ss)
    if debug:
        print(time.time())
        print(msg)
    ser.write(msg)

def main(args = parseArgs()):
    try:
        sync = False
        c = 30
        ser = serial.Serial(args.dev, 9600)
        s = sched.scheduler(time.time, time.sleep)
        while True:
            s.enterabs(int(time.time()) + 1, 1, sendTime, 
                kwargs={'ser': ser, 'sync': sync, 'utc': args.utc, 'debug': args.debug})
            s.run()
            if c > 15:
                sync = checkNtpSync()
                if args.debug:
                    print(f"NTP status: {sync}")
                c = 0
            c += 1
    except KeyboardInterrupt:
        print("Exiting...")
        ser.close

if __name__ == "__main__":
    main()
