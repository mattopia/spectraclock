# spectraclock.py

A Spectracom "Format 1" time message format emulator.  Messages are sent at the top of every second and output to a serial port.  This is useful for feeding time data to Spectracom clocks.  This script has been tested on various Raspberry Pi's and a Spectracom model 8177 TimeView 400 LED clock.  It should work on any UNIX-y platform with any devices that support "Format 1" messages.

# Background 

I have an obsession with interesting clocks and acquired a Spectracom 8177 TimeView 400 clock from eBay.  It was previously installed in a 911 call center, and it was now in my basement.  The TimeView 400 can be manually set and seems to keep relatively good time on its own, but it's designed to synchronize with a master clock, such as NetClock models 9183 or 9188.  I wanted to keep the clock synchronized witout the use of wiring or external devices.  I wanted to use a microcontroller, such as a Raspberry Pi, to keep the clock synchronized with a time (NTP) server.

Two pieces of glue would be necessary to make this happen.  First, the physical glue -- connecting a Raspberry Pi to the clock.  The TimeView 400 uses an RS-485 connection, and the Raspberry Pi's onboard serial ports use TTL (0 - 5 volt) logic levels.  A number of converters are readily available on Amazon for this purpose, most for under $10.  This made the physical glue pretty much plug and play.

Second, the software glue.  The TimeView 400 expects incoming messages every second that indicate the current date and time.  The device supports two protocols, called simply "Format 0" and "Format 1".  Thankfully, both formats are fairly well documented in the instruction manuals for the master clock devices.  Both formats appeared fairly simple to construct, however Format 1 seemed a bit easier.  And thus, this script was born.

# Hardware Requirements

First, you'll need a computer.  Preferably something cheap and small.  The Raspberry Pi Zero W is ideal.

Obviously you need a clock or other devices that expects the Spectracom Format 1 type messages.  You'll also need a converter of some type to convert the serial output of your device to the RS-485 connection that your device (likely) requires.  If you are using a Raspberry Pi, or another SBC / microcontroller that uses 3.3v or 5v TTL levels, this is the one I used:

https://www.amzn.com/B07B667STP

If your computer outputs RS-232 (i.e. a traditional DB-9 serial port), there are RS-232 to RS-485 readily available as well.

# Software Requirements

This script was written in and tested with Python 3.7.  It uses five modules, four of which are part of the standard library.  The fifth, _serial_, must be installed.  On Raspbian, this can be accomplished by running the following:

```sudo apt install python3-serial```

You will want to make sure your computer is configured to synchronize with an NTP server.  Most modern Linux distributions, including Raspbian, use _systemd-timesyncd_ to keep time synchronized.  It's OK, but not great.  I recommend disabling it and installing _chrony_. 

```
sudo sudo systemctl disable systemd-timesyncd
sudo systemctl stop systemd-timesyncd
sudo apt install chrony
```

The default chrony configuration should be sufficient, however you are encouraged to research and modify the configuration to your liking.  
