# This is a rework of the RoboArm - Simple interface, allowing the motors to be run at the same time, and fully
# adopting the correct API, allowing for other operators to use it correctly, without sending invalid commands to the system.

# OWI-535 Robotic Arm - Advanced Web Interface and Controller / Python + Bottle

import os
from bottle import Bottle, run, static_file
import usb.core
import usb.util


def motormsk(motor_id, motor_config):
  return (motor_config[motor_id][0][0] | motor_config[motor_id][1][0], motor_config[motor_id][0][1] | motor_config[motor_id][1][1], motor_config[motor_id][0][2] | motor_config[motor_id][1][2])

def motorcmb(motor_id_1, motor_dir_1, motor_id_2, motor_dir_2, motor_config):
  return (motor_config[motor_id_1][motor_dir_1][0] | motor_config[motor_id_2][motor_dir_2][0], motor_config[motor_id_1][motor_dir_1][1] | motor_config[motor_id_2][motor_dir_2][1], motor_config[motor_id_1][motor_dir_1][2] | motor_config[motor_id_2][motor_dir_2][2])


# MOTORS: all, m1, m2, m3, m4, m5 (+, -)
MOTORS = (
  (
    (0b01010101, 0b00000001, 0b00000000),
    (0b10101010, 0b00000010, 0b00000000)
  ),
  (
    (0b00000001, 0, 0),
    (0b00000010, 0, 0)
  ),
  (
    (0b00000100, 0, 0),
    (0b00001000, 0, 0)
  ),
  (
    (0b00010000, 0, 0),
    (0b00100000, 0, 0)
  ),
  (
    (0b10000000, 0, 0),
    (0b01000000, 0, 0)
  ),
  (
    (0, 0b00000001, 0),
    (0, 0b00000010, 0)
  )
)

LED = ((0, 0, 1), (0, 0, 0))

# TRACKS: both, right, left (forward, reverse)
TRACKS = (
  (
    motorcmb(4, 0, 5, 0, MOTORS),
    motorcmb(4, 1, 5, 1, MOTORS)
  ),
  MOTORS[4],
  MOTORS[5]
)

# ARM: all, elbow, wrist, grip (forward/open, reverse/close)
ARM = (
  (
    motorcmb(0, 0, 1, 0, ((motorcmb(1, 0, 2, 0, MOTORS), motorcmb(1, 1, 2, 1, MOTORS)), (MOTORS[3]))),
    motorcmb(0, 1, 1, 1, ((motorcmb(1, 0, 2, 0, MOTORS), motorcmb(1, 1, 2, 1, MOTORS)), (MOTORS[3])))
  ),
  MOTORS[3],
  MOTORS[2],
  MOTORS[1]
)

OWI535USB = {
  "description": "OWI-535 Robotic Arm - USB Interface",
  "identification": {
    "description": "These are the parameters used to identify the RoboArm using the USB connection",
    "idVendor": 0x1267,
    "idProduct": 0x000
  },
  "initialisation": {
    "description": "These variables are used to transfer data on the created USB connection",
    "bmRequestType": 0x40,
    "bmRequest": 6,
    "wValue": 0x100,
    "wIndex": 0
  }
}

ROVER = {
  "components": {
    "tracks": {
      "description": "The <ARM> components are mounted on this rotating tracked system",
      "mask": motormsk(0, TRACKS),
      "features": {
        "both": {
          "description": "This is a pseudo-feature that allows for motor controls for the tracks - it should cover all the needs for the tracks as running them individually isn't efficient",
          "mask": motormsk(0, TRACKS),
          "verbs": {
            "stop": motormsk(0, TRACKS),
            "forward": TRACKS[0][0],
            "reverse": TRACKS[0][1],
            "turncw": motorcmb(1, 0, 2, 1, TRACKS),
            "turnccw": motorcmb(1, 1, 2, 0, TRACKS)
          }
        }
      }
    },
    "arm": {
      "description": "This component is mounted on the <BASE>, and replicates a typical human arm - with features, i.e. shoulder, elbow, wrist and a gripper.",
      "mask": motormsk(0, ARM),
      "features": {
        "all": {
          "description": "This is a pseudo-feature that allows for complex functions to be predescribed for the whole <ARM> component",
          "mask": motormsk(0, ARM),
          "verbs": {
            "stop": motormsk(0, ARM)
          }
        },
        "elbow": {
          "description": "",
          "mask": motormsk(1, ARM),
          "verbs": {
            "open": ARM[1][0],
            "close": ARM[1][1],
            "stop": motormsk(1, ARM)
          }
        },
        "wrist": {
          "description": "",
          "mask": motormsk(2, ARM),
          "verbs": {
            "open": ARM[2][0],
            "close": ARM[2][1],
            "stop": motormsk(2, ARM)
          }
        },
        "grip": {
          "description": "",
          "mask": motormsk(3, ARM),
          "verbs": {
            "open": ARM[3][1],
            "close": ARM[3][0],
            "stop": motormsk(3, ARM)
          }
        }
      }
    },
    "light": {
      "description": "This is an LED mounted behind the <GRIP> feature on the <ARM> component - the focus of the light is useful to highlight where to grab, or that the system is in use",
      "mask": LED[0],
      "features": {
        "switch": {
          "description": "The only feature of the <LIGHT> is the <SWITCH>, simply flipping the last bit of the 3rd byte",
          "mask": LED[0],
          "verbs": {
            "on": LED[0],
            "off": LED[1]
          }
        }
      }
    }
  }
}

# Global motor state - mutated in place by each command request.
# Note: Bottle's default server is single-threaded, which keeps this safe.
move_command = [0, 0, 0]


def change_move_command(update_move_command, roboarm_components_system, component, feature, verb):
  # check that the input is valid against the roboarm_components_system inputs
  input_exists = check_inputs(roboarm_components_system, component, feature, verb)

  if input_exists[0]:
    # when receiving all valid inputs we should be cancelling out the current movement using the mask for the associated level (e.g. feature mask)
    # this is achieved through the the logical AND(&) with the logical NOT(~) of the mask
    update_move_command[0] = (update_move_command[0] & ~roboarm_components_system[component]["features"][feature]["mask"][0])
    update_move_command[1] = (update_move_command[1] & ~roboarm_components_system[component]["features"][feature]["mask"][1])
    update_move_command[2] = (update_move_command[2] & ~roboarm_components_system[component]["features"][feature]["mask"][2])
    # the return_move_command is further updated through the logical OR(|) with the desired movement - this leaves the existing values unchanged
    update_move_command[0] = (update_move_command[0] | roboarm_components_system[component]["features"][feature]["verbs"][verb][0])
    update_move_command[1] = (update_move_command[1] | roboarm_components_system[component]["features"][feature]["verbs"][verb][1])
    update_move_command[2] = (update_move_command[2] | roboarm_components_system[component]["features"][feature]["verbs"][verb][2])

  return update_move_command, input_exists


def check_inputs(roboarm_components_system, component, feature, verb):
  component_exists = component in roboarm_components_system
  feature_exists = component_exists and feature in roboarm_components_system[component]["features"]
  verb_exists = feature_exists and verb in roboarm_components_system[component]["features"][feature]["verbs"]
  return (component_exists and feature_exists and verb_exists), component_exists, feature_exists, verb_exists


def initialise_robocontroller(vendor_id=OWI535USB["identification"]["idVendor"], product_id=OWI535USB["identification"]["idProduct"]):
  try:
    robocontroller = usb.core.find(idVendor=vendor_id, idProduct=product_id)
    print(f"INFO: initialised device: vendor_id={vendor_id}, product_id={product_id}")
    print(f"INFO: device: robocontroller={robocontroller}")
    return robocontroller
  except Exception as e:
    print(f"ERROR: unable to find device: vendor_id={vendor_id}, product_id={product_id}")
    print(f"ERROR: exception={e}")
    return None


_robocontroller = initialise_robocontroller()


def transfer_robocontroller(move_command, ctrl_roboarm=OWI535USB["initialisation"], timeout=1000):
  global _robocontroller
  transfer_stats = None

  if _robocontroller is None:
    print("WARN: Reinitialising robocontroller")
    _robocontroller = initialise_robocontroller()

  if _robocontroller is not None:
    try:
      transfer_stats = _robocontroller.ctrl_transfer(ctrl_roboarm["bmRequestType"], ctrl_roboarm["bmRequest"], ctrl_roboarm["wValue"], ctrl_roboarm["wIndex"], move_command, timeout)
    except Exception as e:
      print(f"ERROR: unable to update device with ctrl: move_command={move_command}")
      print(f"ERROR: exception={e}")

  return transfer_stats


app = Bottle()

_INTERFACE_ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'interface')


def build_config():
  config = {"description": "Giraffe Rover", "components": {}}
  for comp_name, comp in ROVER["components"].items():
    features = {}
    for feat_name, feat in comp["features"].items():
      features[feat_name] = {
        "description": feat.get("description", ""),
        "actions": {verb: list(cmd) for verb, cmd in feat["verbs"].items()}
      }
    config["components"][comp_name] = {
      "description": comp.get("description", ""),
      "features": features
    }
  return config


@app.route('/config')
def get_config():
  return build_config()


@app.route('/roboarm/<component>/<feature>/<verb>')
def move_roboarm(component, feature, verb):
  print(f"request: component={component}, feature={feature}, verb={verb}")
  print(f"current move_command:{move_command}")

  change_move_command(move_command, ROVER["components"], component, feature, verb)

  print(f"new move_command:{move_command}")

  transfer_attempt = transfer_robocontroller(move_command)
  print(f"transfer_attempt:{transfer_attempt}")

  return move_command[0]


@app.route('/interface/<filepath:path>')
def server_static(filepath):
  return static_file(filepath, root=_INTERFACE_ROOT)


run(app, host='0.0.0.0', port=8888)
