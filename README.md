# giraffe-rover

Software and build instructions for a Raspberry Pi powered rover, featuring a spotlight, robotic arm and tracked base — controlled via a web interface with live video feedback.

---

## What It Does

Giraffe-rover lets you remotely control a physical robot from a browser (including iOS). The robot consists of:

- **Tracked base** — moves forward, reverse, turns clockwise/counterclockwise
- **Robotic arm (OWI-535)** — elbow, wrist, and gripper joints
- **LED spotlight** — mounted behind the gripper to illuminate the target area
- **Live camera feed** — MJPEG stream embedded in the control interface

The key improvement over simpler implementations is that multiple motors can run simultaneously. Commands are composed via bitmask operations rather than sent sequentially, so e.g. the arm can move while the rover is driving.

---

## Hardware Requirements

| Component | Details |
|-----------|---------|
| Raspberry Pi | Zero W (or similar), running Raspbian |
| Camera module | Any RPi-compatible camera |
| Robotic arm | OWI-535 Robotic Arm Edge (USB interface version) |
| USB connection | OWI-535 plugged into the Pi via USB |

---

## Software Prerequisites

Install Python dependencies:

```bash
sudo pip3 install -r requirements.txt
```

Install and configure the camera stream:

1. Install [RPi-Cam-Web-Interface](https://elinux.org/RPi-Cam-Web-Interface)
2. In the Advanced/default interface, go to **System** and switch the stream type from `Default-Stream` to `MJPEG-Stream`
3. The MJPEG stream will then be embeddable in the web interface

---

## Running

Clone the repository onto the Pi, then:

```bash
sudo python3 giraffe-rover.py
```

Navigate to:

```
http://your-device-hostname.local:8888/interface/index.html
```

---

## Architecture

### Overview

```
Browser
  │  (HTTP GET /roboarm/<component>/<feature>/<verb>)
  ▼
giraffe-rover.py  (Bottle web server, port 8888)
  │  (3-byte bitmask command)
  ▼
PyUSB ctrl_transfer
  │
  ▼
OWI-535 USB Interface  →  Motors / LED
```

---

### Backend: `giraffe-rover.py`

The backend is a single Python file that handles both USB motor control and HTTP serving.

#### USB Motor Protocol

The OWI-535 arm is controlled by sending 3-byte USB control transfers. Each byte is a bitmask where individual bits correspond to individual motor channels:

| Byte | Controls |
|------|---------|
| Byte 0 | Arm motors (elbow, wrist, grip, base rotation) — bits 0–7 |
| Byte 1 | Track motors (left and right) — bits 0–1 |
| Byte 2 | LED — bit 0 |

Each motor has two directions (forward/reverse), each mapped to a specific bit. To stop a motor, both its bits are cleared.

#### Bitmask Composition

Two utility functions handle command composition:

- **`motormsk(motor_id, motor_config)`** — ORs both directions of a motor together to produce its full bitmask (used for masking out a motor's bits before writing a new state)
- **`motorcmb(motor_id_1, dir_1, motor_id_2, dir_2, motor_config)`** — ORs two motors' directional commands together into a single combined command (used for simultaneous movement, e.g. both tracks forward)

#### Motor Definitions

```
MOTORS[0]  — all arm motors combined (convenience alias)
MOTORS[1]  — grip
MOTORS[2]  — wrist
MOTORS[3]  — elbow
MOTORS[4]  — right track
MOTORS[5]  — left track

LED        — spotlight (byte 2, bit 0)
```

These are assembled into two higher-level groups:

- **`TRACKS`** — `(both, right, left)` × `(forward, reverse)`, derived from MOTORS[4] and MOTORS[5]
- **`ARM`** — `(all, elbow, wrist, grip)` × `(open/forward, close/reverse)`, derived from MOTORS[1–3]

#### ROVER Configuration

The `ROVER` dict is the source of truth for the command API. It has three components:

```
tracks
  └── both
        ├── forward
        ├── reverse
        ├── turncw
        ├── turnccw
        └── stop

arm
  ├── all     (stop only — virtual aggregate)
  ├── elbow   (open / close / stop)
  ├── wrist   (open / close / stop)
  └── grip    (open / close / stop)

light
  └── switch
        ├── on
        └── off
```

#### Command Execution: `change_move_command`

The server maintains a persistent `move_command = [0, 0, 0]` list (the current motor state). When a request arrives:

1. The feature's **mask** is used to zero out only that feature's bits: `cmd & ~mask`
2. The verb's **value** is then ORed in: `cmd | verb_value`
3. This preserves all other motors' current states

This is what enables simultaneous motor operation — each command surgically updates only its relevant bits.

#### REST API

```
GET /roboarm/<component>/<feature>/<verb>
```

Returns the updated byte 0 of the move command as plain text.

Examples:

```
GET /roboarm/tracks/both/forward     — drive forward
GET /roboarm/tracks/both/turncw      — turn clockwise
GET /roboarm/arm/grip/open           — open gripper
GET /roboarm/arm/elbow/close         — lower elbow
GET /roboarm/light/switch/on         — turn spotlight on
GET /roboarm/arm/all/stop            — stop all arm motors
```

```
GET /interface/<filepath>            — serves static frontend files
```

---

### Frontend: `interface/`

The frontend is a React app served as static files by Bottle. React, ReactDOM, and Grommet are loaded from CDN. `interface/js/index.js` is the compiled output — the source of truth is `interface/babel/index.babel` (JSX + ES6 class properties), which should be compiled to `index.js` whenever it changes.

#### Component Hierarchy

```
RoboArmApp                     (root — state, API calls)
  └── Topology                 (Grommet visual diagram)
        └── RoboArmComponents  (iterates over ROVER components)
              ├── RoboArmComponentFeatures   (left column — clickable feature nodes)
              └── RoboArmControlFeatures     (right column — clickable action nodes)
                    └── RoboArmControlFeatureActions
```

#### Interaction Model

The UI renders the rover's component/feature/verb hierarchy as a Grommet `Topology` diagram — a visual graph where nodes are connected by links.

Sending a command is a two-click interaction:

1. Click a **feature node** (e.g. `arm → grip`) — stored in state as `clicked_items[0]`
2. Click an **action node** (e.g. `arm → open`) — stored as `clicked_items[1]`

When both are from the same component, `update_links` fires, updates the visual connector line, and calls `invoke_api`:

```
fetch(`/roboarm/${component}/${feature}/${action}`)
```

The response updates the displayed `move_command` state.

#### Live Video

The MJPEG feed from RPi-Cam-Web-Interface is embedded as an `<img>` tag pointing to `/html/cam_pic_new.php` on the same hostname (port 80), which refreshes automatically.

---

---

## Frontend Build

The JSX source lives in `interface/babel/index.babel`. After editing it, compile to `interface/js/index.js` using Babel. You only need Node.js for this step — it runs on any machine, not the Pi.

**Install build dependencies (once):**

```bash
npm install
```

**Compile:**

```bash
npm run build
```

Then copy or sync the updated `interface/js/index.js` to the Pi alongside the rest of the interface directory.

The `package.json` uses `@babel/cli` with `@babel/preset-react` (JSX) and `@babel/preset-env` (ES6→ES5 for broad browser compatibility), plus `@babel/plugin-proposal-class-properties` for the arrow-function method syntax.

> **Note:** Do not edit `interface/js/index.js` directly — it will be overwritten on the next build.

---

## Project Structure

```
giraffe-rover/
├── giraffe-rover.py          # Backend: Bottle server + USB motor control
├── requirements.txt          # Python dependencies
├── package.json              # Frontend build tooling (Babel)
├── .gitignore
└── interface/
    ├── index.html            # Frontend entry point (loads CDN deps + index.js)
    ├── css/
    │   └── style.css         # Topology node and layout styles
    ├── js/
    │   ├── index.js          # Compiled output — do not edit directly
    │   └── oojjnj.js         # Grommet/Topology utility shim
    └── babel/
        └── index.babel       # JSX source — edit this, then run npm run build
```

---

## License

MIT — Copyright 2018, Jaison Miller
