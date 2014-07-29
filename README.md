enjigo_door
===========

An rfid/nfc door unlocking system, complete with web-based account manager. Super simple, barely beta quality. Powered by Google App Engine. Written in python for the raspberry pi, and as a Django app for the server-side stuff.

You are welcome to use it, but I would wait until June 2014, when we release it for reals.

History & plans
===========

Hello there, somehow you've stumbled upon the rfid door control software for Enjigo, Salt Lake's premiere Makerspace.
We are currently using this software in our door for members. Our/My end goal is to release it to the public free of charge, along with 3d models and tutorials on building hardware to control a door.

#####phase 1) (6 months)
was a custom designed arduino knockoff that stored accounts in eeprom. we ran out of eeprom, and wanted web access. So I took over the project and started phase 2.

####phase 2) (2 months)
I hacked the software of the arduino to add serial communication so old members could use the door uninterupted while I added web based, raspberry pi control and user accounts. The user account system owrked swimmingly, so, after a month (these things should be tested, and I am wicked busy), i started...

####phase 3) (1 month)
a complete replacement of the hardware. We have a custom raspberry pi "shield" that is essenitally a hand soldered relay, a attiny85 with a light animation library attached for fun user feedbak, and and a spi based nfc module.

We have successfully been using it without a hitch on a stock raspberry pi,and sunfounder spi based nfc modules (for rfid reading), and relays (for 12v lock controlling). links to buy this stuff on Amazon are below. For now, the latest phase...

####phase 4) (2 weeks)
I have started 3d modeling a cover and housing to fit over a standard deadbolt (very similar to lockitron.com) and I have started migrating over a lightweight nodejs server, and the socketio python client stuff so I can add mobile phone and computer triggering. Move off Google App Engine, or remove django.

####phase 5) (1 month)
Admins will use the phones to get in an out with no keys while i finish the 3d printed hardware. 

####phase 6) (1-3 months)
love it or iterate the hardware. make php version for the lame.

####phase 7) approximately June
release to public for free. Sell circuit board kits to those who don't want to get their own printed. Possibily sell pre fabricated ones, if I haven't found somehting better to do - and I likely will.


####install notes to self
enjigo door raspberry pi base setup

install occidetalis
expand, enable ssh
enable wifi : sudo nano /etc/network/interfaces
copy github keys from docs via cyberduck and ssh
install SPI extension

install SPI-py:
git clone https://github.com/lthiery/SPI-Py.git
 cd SPI-Py
 sudo python setup.py install



reference :
https://github.com/mxgxw/MFRC522-python
https://github.com/lthiery/SPI-Py
https://learn.sparkfun.com/tutorials/programming-the-pcduino/spi-communications

get pip working:
sudo apt-get update (needed to pulling misc stuff)


http://www.raspberrypi.org/phpBB3/viewtopic.php?t=33125&p=284421

reference : http://learn.adafruit.com/send-raspberry-pi-data-to-cosm/necessary-packages


install requests:
sudo rebasheasy_install requests
sudo apt-get install python-pip
install blinkm linrary : 
sudo pip install pyblinkm

install socket io client for node
sudo pip install -U socketIO-client


reference : https://github.com/tsileo/pyblinkm

copy sounds over to /home/pi/sounds/


get it working on startup
resize text to fit little screen
have it connect to cell dongle if needed

make autlogin :
http://raspisimon.no-ip.org/rpi_autologin.php

disable serial port logging
http://dav3.net/dribble/1180


todo:
add swipe sound ; link coin acquire or something
screen saver
install app into /etc


tips:
sudo apt-get update : updates system
sudo raspi-config : gets you to setup screen


sudo i2cdetect -y 1: find connected i2c devices:


sudo shutdown -h now
