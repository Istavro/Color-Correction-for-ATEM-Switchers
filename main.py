import PyATEMMax
import base64
import hashlib
import json
import websocket
import threading


# Connecting to OBS websocket
host = "127.0.0.1" # IP for OBS
port = 4455 # Port for OBS websocket
password = "0f9ZuuGXia3rHBnQ"

id = 1

ws = websocket.WebSocket()
url = "ws://{}:{}".format(host, port)
ws.connect(url)

def build_auth_string(salt, challenge):
    secret = base64.b64encode(
        hashlib.sha256(
            (password + salt).encode('utf-8')
        ).digest()
    )
    auth = base64.b64encode(
        hashlib.sha256(
            secret + challenge.encode('utf-8')
        ).digest()
    ).decode('utf-8')
    return auth



def auth():
    message = ws.recv()
    result = json.loads(message) 
    server_version = result['d'].get('obsWebSocketVersion')
    auth = build_auth_string(result['d']['authentication']['salt'], result['d']['authentication']['challenge'])

    payload = {
        "op": 1,
        "d": {
            "rpcVersion": 1,
            "authentication": auth,
            "eventSubscriptions": 1000 
        }
    }
    ws.send(json.dumps(payload))
    message = ws.recv()
    result = json.loads(message)

auth()

# Connecting to switcher
switcher = PyATEMMax.ATEMMax()
switcher.connect("127.0.0.1") # IP of the switcher
switcher.waitForConnection()

# Define the word that will stop the script
breakWord = "stop"
# Initialize a flag to control the loop
stopFlag = threading.Event()

def checkInput():
    global stopFlag
    while True:
        # Get user input from the command line
        userInput = input()
        # Check if the input matches the break word
        if userInput.strip().lower() == breakWord:
            stopFlag.set()
            break

# Start the input checking thread
inputThread = threading.Thread(target=checkInput)
inputThread.daemon = True
inputThread.start()

# Logic to switch filters as PGM source is switched.
previousSource = str(switcher.programInput[0].videoSource)

while not stopFlag.is_set():
    currentSource = str(switcher.programInput[0].videoSource)

    if currentSource != previousSource:
        # Disable previous source filter
        ws.send(json.dumps({
            "op" : 6,
            "d" : {
                "requestId" : "DisableFilter",
                "requestType" : "SetSourceFilterEnabled",
                "requestData" : {
                    "sourceName" : "Display Capture",
                    "filterName" : previousSource,
                    "filterEnabled" : False
                }
            }
        }))
        # Enable current source filter
        ws.send(json.dumps({
            "op" : 6,
            "d" : {
                "requestId" : "EnableFilter",
                "requestType" : "SetSourceFilterEnabled",
                "requestData" : {
                    "sourceName" : "Display Capture",
                    "filterName" : currentSource,
                    "filterEnabled" : True
                }
            }
        }))
        previousSource = currentSource

ws.close() # Disconnect from OBS websocket
switcher.disconnect() # Disconnect from switcher
print("Connections closed")