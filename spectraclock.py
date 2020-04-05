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
    p.add_argument('--ntp', type=int, default=0, help='Check NTP interval, disabled by default.')
    return p.parse_args()

def checkNtpSync(debug = False):
    # Check synchronization status of a local chrony NTP service
    # Returns true if synchronized within +/- 0.1 second offset
    p = subprocess.Popen(['chronyc', '-c', 'tracking'], stdout=subprocess.PIPE)
    try:
        output = p.communicate(timeout = 0.1)[0]
        if debug:
            print(output.decode())
    except subprocess.TimeoutExpired:
        print("NTP Check - Timeout Exceeded")
        p.kill()
        return False
    if p.returncode == 0:
        refclock = output.decode().split(",")[0]
        offset = float(output.decode().split(",")[4])
        if refclock != "00000000" and offset < 0.1 and offset > -0.1:
            return True
        else:
            return False
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

def sendTime(ser, sync = True, debug = False):
    ss = " " if sync else "?"
    msg = formatTime(time.localtime(), ss)
    ser.write(msg)
    if debug:
        print(time.time())
        print(msg)

def main(args = parseArgs()):
    try:
        sync = True
        ser = serial.Serial(args.dev, 9600)
        c = args.ntp
        s = sched.scheduler(time.time, time.sleep)
        while True:
            if args.ntp > 0:
                c += 1
            if c > args.ntp:
                sync = checkNtpSync(args.debug)
                if args.debug:
                    print(f"NTP status: {sync}")
                c = 0
            s.enterabs(int(time.time()) + 1, 1, sendTime, 
                kwargs={'ser': ser, 'sync': sync, 'debug': args.debug})
            s.run()
    except KeyboardInterrupt:
        print("Exiting...")
        ser.close

if __name__ == "__main__":
    main()
