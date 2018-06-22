# This is a rework of the RoboArm - Simple interface, allowing the motors to be run at the same time, and fully
# adopting the correct API, allowing for other operators to use it correctly, without sending invalid commands to the system.

# OWI-535 Robotic Arm - Advanced Web Interface and Controller / Python + Bottle

# imports
from bottle import Bottle, run, template, request, static_file
import usb.core, usb.util

def motormsk (motor_id, motor_config):
  return (motor_config[motor_id][0][0] | motor_config[motor_id][1][0], motor_config[motor_id][0][1] | motor_config[motor_id][1][1], motor_config[motor_id][0][2] | motor_config[motor_id][1][2])
  
def motorcmb (motor_id_1, motor_dir_1, motor_id_2, motor_dir_2, motor_config):
  return (motor_config[motor_id_1][motor_dir_1][0] | motor_config[motor_id_2][motor_dir_2][0], motor_config[motor_id_1][motor_dir_1][1] | motor_config[motor_id_2][motor_dir_2][1], motor_config[motor_id_1][motor_dir_1][2] | motor_config[motor_id_2][motor_dir_2][2])

# MOTORS: all, m1, m2, m3, m4, m5 (+, -)
MOTORS = (
  (
    (0b01010101, 0b00000001, 0b00000000),
    (0b10101010, 0b00000010, 0b00000000)
  ),
  (
    (2**0, 0, 0),
    (2**1, 0, 0)
  ),
  (
    (2**2, 0, 0),
    (2**3, 0, 0)
  ),
  (
    (2**4, 0, 0),
    (2**5, 0, 0)
  ),
  (
    (2**7, 0, 0),
    (2**6, 0, 0)
  ),
  (
    (0, 2**0, 0),
    (0, 2**1, 0)
  )
)

LED = ((0,0,1),(0,0,0))

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
      motorcmb(0, 0, 1, 0,((motorcmb(1, 0, 2, 0, MOTORS),motorcmb(1, 1, 2, 1, MOTORS)),(MOTORS[3]))),
      motorcmb(0, 1, 1, 1,((motorcmb(1, 0, 2, 0, MOTORS),motorcmb(1, 1, 2, 1, MOTORS)),(MOTORS[3])))
    ),
    MOTORS[3],
    MOTORS[2],
    MOTORS[1]
  )

OWI535USB = {
  "description": "OWI-535 Robotic Arm - USB Interface",
  "identification":{
    "description":"These are the parameters used to identify the RoboArm using the USB connection",
    "idVendor": 0x1267,
    "idProduct": 0x000
  },
  "initialisation":{
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
          "description":"",
          "mask": motormsk(1, ARM),
          "verbs": {
            "open": ARM[1][0],
            "close": ARM[1][1],
            "stop": motormsk(1, ARM)
          }
        },
        "wrist": {
          "description":"",
          "mask": motormsk(2, ARM),
          "verbs": {
            "open": ARM[2][0],
            "close": ARM[2][1],
            "stop": motormsk(2, ARM)
          }
        },
        "grip": {
          "description":"",
          "mask": motormsk(3, ARM),
          "verbs": {
            "open": ARM[3][1],
            "close": ARM[3][0],
            "stop": motormsk(3, ARM)
          }
        },
      }
    },
    "light": {
      "description":"This is an LED mounted behind the <GRIP> feature on the <ARM> component - the focus of the light is useful to highlight where to grab, or that the system is in use",
      "mask": LED[0],
      "features": {
        "switch": {
          "description":"The only feature of the <LIGHT> is the <SWITCH>, simply flipping the last bit of the 3rd byte",
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

# initialise the global vars
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
  
  # calling the function just returns the updated dict {} and doesn't affect any data outside of the function, or use any data that is not passed in
  return update_move_command, input_exists
  
def check_inputs(roboarm_components_system, component, feature, verb):
  # print(component in roboarm_components_system.keys())
  component_exists = component in roboarm_components_system.keys()
  # print(feature in roboarm_components_system[component]["features"].keys())
  feature_exists = feature in roboarm_components_system[component]["features"].keys()
  # print(verb in roboarm_components_system[component]["features"][feature]["verbs"].keys())
  verb_exists = verb in roboarm_components_system[component]["features"][feature]["verbs"].keys()
  
  # return the complete list of the 
  return (component_exists & feature_exists & verb_exists), component_exists, feature_exists, verb_exists

def initialise_robocontroller(vendor_id=OWI535USB["identification"]["idVendor"], product_id=OWI535USB["identification"]["idProduct"]):

  try:
    robocontroller = usb.core.find(idVendor=vendor_id, idProduct=product_id)
    print("INFO: initialised device: vendor_id={}, product_id={}".format(vendor_id, product_id))
    print("INFO: device: robocontroller={}".format(robocontroller))
    return robocontroller
  except Exception as e:
    print("ERROR: unable to find device: vendor_id={}, product_id={}".format(vendor_id, product_id))
    print("ERROR: exception={}".format(e))
    return None


initial_robocontroller_device = initialise_robocontroller()
  
def transfer_robocontroller(move_command, ctrl_roboarm=OWI535USB["initialisation"], timeout=1000, robocontroller_device=initial_robocontroller_device):
  transfer_stats = None

  if robocontroller_device is None:
      # attempt to initialise the device 
    print("WARN: Reinitialising robocontroller")
    robocontroller_device = initialise_robocontroller()
  else:
  
  # perform the actual USB transfer, returning the length of the transfer
    try: 
      transfer_stats = robocontroller_device.ctrl_transfer(ctrl_roboarm["bmRequestType"], ctrl_roboarm["bmRequest"], ctrl_roboarm["wValue"], ctrl_roboarm["wIndex"], move_command, timeout)
    except Exception as e:
      print("ERROR: unable to update device with ctrl: move_command={}".format(move_command))
      print("ERROR: exception={}".format(e))
      
  return transfer_stats

app = Bottle()

@app.route('/roboarm/<component>/<feature>/<verb>')
def move_roboarm(component, feature, verb, move_command=move_command):
  
  # print out the input parameters
  print("request: component={}, feature={}, verb={}".format(component, feature, verb))
  
  # print out the current move command
  print("current move_command:{}".format(move_command))
  
  # update the move_command dictionary
  move_command = change_move_command(move_command, ROVER["components"], component, feature, verb)[0]
  
  # print out the updated move command
  print("new move_command:{}".format(move_command))
  
  # make the transfer
  transfer_attempt = transfer_robocontroller(move_command)
  
  # print out the result
  print("transfer_attempt:{}".format(transfer_attempt))

  # return the current move command
  return move_command[0]
  
@app.route('/interface/<filepath:path>')
def server_static(filepath):
    return static_file(filepath, root='/home/pi/rover/roboarm/interface')

run(app, host='0.0.0.0', port=8888)





