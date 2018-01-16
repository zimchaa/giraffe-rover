# giraffe-rover
Software and build instructions for a Raspberry Pi powered rover, featuring a spotlight, robotic arm and tracked base - controlled via a web interface with video feedback.

Instructions

Environment: Running on a Raspberry Pi (Zero W) - running Raspbian (latest), with a Camera module plugged in, and the USB controlled motor interface from the OWI 535, Robotic Arm Edge (from Maplin) plugged in.

---
Install the latest PyUSB and Bottle modules using PIP:

    > sudo pip3 install bottle
    > sudo pip3 install --pre pyusb

Install the latest RPi-Cam-Web-Interface: https://elinux.org/RPi-Cam-Web-Interface - when this is running, change the stream type (using the Advanced/default interface) in the 'System' submenu from 'Default-Stream' to 'MJPEG-Stream' by clicking the button, it should reload the interface showing the MJPEG video stream that would allow you to embed it in the web interface.

Clone and download the giraffe-rover repository - and then run the interface:

    > sudo python3 giraffe-rover.py

Navigate (works on iOS) to http://your-device-hostname.local:8888/interface/index.html and have fun controlling the rover remotely.
