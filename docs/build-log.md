# Giraffe Rover — Build Log

A build log for the Giraffe Rover: a Raspberry Pi Zero W controlled tracked robot with an OWI-535 robotic arm, LED spotlight, and live camera feed operated from a browser.

---

## Bill of Materials

| Part | Notes |
|------|-------|
| Raspberry Pi Zero W | Main controller — runs Python/Bottle server on port 8888 |
| RPi Camera Module | Any RPi-compatible camera; used for MJPEG live feed |
| OWI-535 Robotic Arm Edge (USB version) | 5-motor arm: base rotation, elbow, wrist, grip + LED |
| Tracked base chassis | Houses the drive gearbox and dual track motors |
| USB cable | Connects OWI-535 to the Pi |
| Power supply | Powers both Pi and arm via USB |
| LED spotlight | Mounted behind gripper on the OWI-535 arm |

---

## Stage 1 — Track Drive System

The tracked base provides the mobility platform. Two independent motors drive the left and right tracks, allowing forward, reverse, and differential steering (clockwise/counterclockwise turns by running tracks in opposite directions).

### 1.1 Drive Gearbox

The gearbox sits at the rear of the chassis, beneath the Raspberry Pi mount. It steps down motor speed to usable torque for the tracks.

<!-- Upload image: rear gearbox assembly, track drive motor visible -->
![Track drive gearbox — rear view](images/01-track-gearbox-rear.jpg)

<!-- Upload image: gearbox detail / gear train -->
![Gearbox detail](images/02-track-gearbox-detail.jpg)

<!-- Upload image: gearbox mounted in chassis from above -->
![Gearbox mounted in chassis](images/03-track-gearbox-mounted.jpg)

### 1.2 Track Assembly

<!-- Upload image: track and sprocket fitting -->
![Track and sprocket assembly](images/04-track-sprocket.jpg)

<!-- Upload image: completed track run, side profile -->
![Track run — side profile](images/05-track-run-side.jpg)

<!-- Upload image: both tracks fitted, chassis from front -->
![Both tracks fitted](images/06-tracks-both-fitted.jpg)

---

## Stage 2 — Chassis and Mounting Points

<!-- Upload image: bare chassis from above, showing RPi mounting point above gearbox -->
![Chassis top view — RPi mounting point](images/07-chassis-top.jpg)

<!-- Upload image: chassis from underneath -->
![Chassis underside](images/08-chassis-underside.jpg)

---

## Stage 3 — Raspberry Pi Zero W

The Pi Zero W is mounted directly above the rear gearbox. It runs the combined HTTP and USB control server (`giraffe-rover.py`) using `waitress` for multi-threaded request handling — essential so the long-lived MJPEG `/stream` connection does not block motor command requests.

### 3.1 Pi Mounting

<!-- Upload image: Pi Zero W before mounting, showing GPIO pins / USB ports -->
![Raspberry Pi Zero W — before mounting](images/09-rpi-premount.jpg)

<!-- Upload image: Pi mounted on chassis above gearbox -->
![Pi mounted above rear gearbox](images/10-rpi-mounted.jpg)

### 3.2 Camera Module

The camera provides a live MJPEG feed embedded in the web interface. The server auto-detects `picamera2` (Bullseye+) or falls back to `picamera` (older Raspbian) at startup.

<!-- Upload image: camera module fitted -->
![Camera module fitted](images/11-camera-fitted.jpg)

<!-- Upload image: camera field of view / angle -->
![Camera angle / field of view](images/12-camera-fov.jpg)

---

## Stage 4 — OWI-535 Robotic Arm

The OWI-535 Robotic Arm Edge (USB interface version) provides five controlled axes plus an LED:

| Motor | Joint | Direction labels |
|-------|-------|-----------------|
| M1 | Grip | open / close |
| M2 | Wrist | open / close |
| M3 | Elbow | open / close |
| M4 | Right track | forward / reverse |
| M5 | Left track | forward / reverse |
| LED | Spotlight | on / off |

All motors are controlled by a single 3-byte USB `ctrl_transfer`. Bits within bytes 0–2 map directly to motor channels, so multiple motors can run simultaneously with a single USB write.

### 4.1 Arm Assembly

<!-- Upload image: OWI-535 unboxed / kit parts -->
![OWI-535 kit parts](images/13-owi535-kit.jpg)

<!-- Upload image: elbow / wrist subassembly -->
![Elbow and wrist subassembly](images/14-owi535-elbow-wrist.jpg)

<!-- Upload image: gripper assembly with LED mount -->
![Gripper and LED mount](images/15-owi535-gripper-led.jpg)

<!-- Upload image: arm fully assembled, pre-mounting -->
![Arm fully assembled](images/16-owi535-assembled.jpg)

### 4.2 Arm Mounted on Chassis

<!-- Upload image: arm mounted on tracked base, side view -->
![Arm mounted on chassis — side](images/17-arm-on-chassis-side.jpg)

<!-- Upload image: arm mounted, front 3/4 view -->
![Arm mounted — front 3/4 view](images/18-arm-on-chassis-front.jpg)

---

## Stage 5 — Wiring and Electronics

<!-- Upload image: USB connection from OWI-535 to Pi -->
![USB connection OWI-535 → Pi](images/19-usb-connection.jpg)

<!-- Upload image: wiring overview / cable routing -->
![Wiring overview](images/20-wiring-overview.jpg)

<!-- Upload image: power supply / battery arrangement -->
![Power supply](images/21-power-supply.jpg)

---

## Stage 6 — Completed Build

<!-- Upload image: completed rover from front -->
![Completed rover — front view](images/22-completed-front.jpg)

<!-- Upload image: completed rover from rear, showing Pi above gearbox -->
![Completed rover — rear view](images/23-completed-rear.jpg)

<!-- Upload image: rover in operation / interface screenshot -->
![Rover in operation](images/24-in-operation.jpg)

---

## Build Notes

### USB Initialisation

The OWI-535 uses vendor ID `0x1267`, product ID `0x0000`. The Pi must run the server with `sudo` to access the USB device without a udev rule:

```bash
sudo python3 giraffe-rover.py
```

On first connection the arm occasionally needs a brief power cycle if the USB device is not found at startup — the server will log `WARN: Reinitialising robocontroller` and retry automatically on the next command request.

### Simultaneous Motor Control

The key design decision is bitmask-based command composition. Each motor has two bits in the 3-byte command array (one per direction). Sending a command zeroes only that motor's bits then ORs in the new direction — all other motors' bits are untouched. This means the arm can move while the rover is driving without any sequencing logic.

### Camera Streaming

The MJPEG stream at `/stream` is a `multipart/x-mixed-replace` response — the browser treats it as a standard `<img>` tag and repaints on each incoming JPEG frame. `waitress` handles this on a separate thread so stream connections don't block motor commands.

---

## Software Setup

See the main [README](../README.md) for full software prerequisites and running instructions.

```bash
# On the Pi:
sudo pip3 install -r requirements.txt
sudo apt install python3-picamera2   # Bullseye+
sudo python3 giraffe-rover.py

# Then open in browser:
http://giraffe.local:8888/interface/index.html
```
