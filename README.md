# spectraclock.py - a script to synchronize Spectracom clocks 

A Spectracom "Format 1" time message format emulator.  Messages are sent at the top of every second and output to a serial port.  This is useful for feeding time data to Spectracom clocks.  This script has been tested on various Raspberry Pi's and a Spectracom model 8177 TimeView 400 LED clock.  It should work on any UNIX-y platform with any devices that support "Format 1" messages.

## Background 

I have an obsession with interesting clocks and acquired a Spectracom 8177 TimeView 400 clock from eBay.  It was previously installed in a 911 call center.  The TimeView 400 can be manually set and seems to keep relatively good time on its own, but it's designed to synchronize with a master clock, such as NetClock models 9183 or 9188.  I wanted to keep the clock synchronized witout the use of wiring or external devices.  I wanted to use a microcontroller, such as a Raspberry Pi, to keep the clock synchronized with a time (NTP) server.

Two pieces of glue are necessary to make this happen.  First, the physical glue -- connecting a Raspberry Pi to the clock.  The TimeView 400 uses an RS-485 connection, and the Raspberry Pi's onboard serial ports use TTL (0 - 5 volt) logic levels.  A number of converters are readily available on Amazon for this purpose, most for under $10.  This made the physical glue pretty much plug and play.

Second, the software glue.  The TimeView 400 expects incoming messages at the top of every second that indicate the current date and time.  The device supports two protocols, called simply "Format 0" and "Format 1".  Thankfully, both formats are fairly well documented in the instruction manuals for the master clock devices.  Both formats appeared fairly simple to construct, however Format 1 seemed a bit easier.  And thus, this script was born.

## Hardware Requirements

First, you'll need a computer.  Preferably something cheap and small.  The Raspberry Pi with wi-fi is ideal.  

Obviously you'll need a clock or other devices that expects the Spectracom Format 1 type messages.  They can be found on eBay at varying prices.  I've seen them listed for hundreds of dollars, but I was able to acquire mine with a "best offer" price of $55.  

You'll also need a converter of some type to convert the serial output of your compute device to the RS-485 connection that your clock (likely) requires.  If you are using a Raspberry Pi, or another SBC / microcontroller that uses 3.3v or 5v TTL levels, this is the one I used.  It conveniently ships with female jumpers as well, making it easy to interface with a Pi.

https://www.amzn.com/B07B667STP

If your computer outputs RS-232 (i.e. a traditional DB-9 serial port), there are RS-232 to RS-485 readily available as well.

## Software Requirements

This script was written in and tested with Python 3.7.  It uses five modules, four of which are part of the standard library.  The fifth, _serial_, must be installed.  On Raspbian, this can be accomplished by running the following:

```sudo apt install python3-serial```

You will want to make sure your computer is configured to synchronize with an NTP server.  Most modern Linux distributions, including Raspbian, use _systemd-timesyncd_ to keep time synchronized.  For increased time accuracy, I recommend disabling it and installing _chrony_ instead.  

```
sudo sudo systemctl disable systemd-timesyncd
sudo systemctl stop systemd-timesyncd
sudo apt install chrony
```

The default chrony configuration should be sufficient, however you are encouraged to research and modify the configuration to your liking.

## Raspberry PI Notes

The Raspberry Pi family of devices are ideal for this purpose.  It's particularly useful that every model includes an on-board serial port.  If you are using a Pi device and the Raspbian Linux distribution, you will likely need to make a few configuration changes to configure the on-board serial port.  Namely, you will want to turn off Bluetooth (optional but recommended) and configure Linux to not use the serial port as a console.  More information can be found here:

https://www.raspberrypi.org/documentation/configuration/uart.md

You will also want to configure Raspbian for the correct time zone.  Raspbian defaults to UTC.  Since this script outputs the time in local time, your attached clock will display the current time in whichever timezone your Pi is configured for.  You can use the `raspi-config` utility to configure the serial port and set the time zone, as well as configure networking, set the system hostname, and more.

Some Pi variants, notably the Zero and Zero W, do not ship with header pins.  If you have one of these variants, you will either need to solder header pins on, or solder wires directly to the correct pins.  

## Installation

1) Download the latest copy of spectraclock.py, place it somewhere convenient, and make it executable:

```
wget https://raw.githubusercontent.com/mattopia/spectraclock/master/spectraclock.py
sudo mv spectraclock.py /usr/local/bin
sudo chmod 755 /usr/local/bin/spectraclock.py
```

2) Manually run the script in debug mode.

```spectraclock.py --debug /dev/ttyAMA0```

Change `/dev/ttyAMA0` to your appropriate serial device.  If you are using a Pi, this should be either `/dev/ttyAMA0` or `/dev/ttyS0`, depending on your configuration.  If you have properly wired your clock, after a few seconds you should see the clock set itself to match your system's current time.  If all is working well, Press Ctrl-C to exit the script.

3) Grab a copy of the example systemd unit file and place it in the appropriate location:

```
wget https://github.com/mattopia/spectraclock/blob/master/spectraclock.service
sudo mv spectraclock.service /etc/systemd/system
```

You may need to edit the `spectraclock.service` file.  Make sure the device name is correct (as tested above).  Also, the service definition by default passes an `--ntp` flag.  This enables a feature that checks to see if chrony is synchronized.  If you're not using chrony, or if you don't wish to use this feature, remove the `--ntp` flag.

4) Enable and start the service.

```
sudo systemctl daemon-reload
sudo systemctl enable spectraclock.service
sudo systemctl start spectraclock.service
```

At this point, you should be all set!  Reboot your pi to make sure everything works after a reboot.  Find a nice way to mount everything and enjoy!
