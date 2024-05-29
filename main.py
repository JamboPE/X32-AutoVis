import PyATEMMax
from pythonosc import udp_client
import time

atem_ip = "144.32.210.206"
X32_ip =  "144.32.210.211"
leftMics = [0,1] # zero indexed lol
rightMics = [2,3] # zero indexed lol
micLevelThreshold = 0

 # Create ATEMMax object
switcher = PyATEMMax.ATEMMax()

# Initialise ATEM variables
preview_id = 2
program_id = 2

class ATEM:
    def connect(ip):
        switcher.connect(ip)
        switcher.waitForConnection()
    def preview(camera_id):
        switcher.setPreviewInputVideoSource(0, camera_id)  # Preview camera_id on ME1
        preview_id = camera_id
    def program(camera_id):
        switcher.setProgramInputVideoSource(0, camera_id)  # Program camera_id on ME1
        program_id = camera_id

def send_osc_command(ip, port, address, *args):
        client = udp_client.SimpleUDPClient(ip, port)
        print(client.send_message(address, args))

if __name__ == "__main__":
    print("Connecting to ATEM switcher...")
    ATEM.connect(atem_ip)
    print("Connected to ATEM switcher")
    print("Setting Program and Preview to Camera 2")
    ATEM.preview(2)
    ATEM.program(2)

    print("Starting AutoVis loop")
    while True:
        print("Checking if VT is playing (checking for mute group 1)...")
        while send_osc_command(X32_ip, 10023, "/config/mute/1") == "OFF": # Only runs autovis if a VT isn't playing (detected based on X32 mute group being on)
            print("Getting mic levels...")
            meters = []
            meters.append(send_osc_command(X32_ip, 10023, "/meters/6 0")) # get levels of mic 1
            meters.append(send_osc_command(X32_ip, 10023, "/meters/6 1")) # get levels of mic 2
            meters.append(send_osc_command(X32_ip, 10023, "/meters/6 2")) # get levels of mic 3
            meters.append(send_osc_command(X32_ip, 10023, "/meters/6 3")) # get levels of mic 4
            print("Mic levels:", meters)

            if switcher.programInput[0].videoSource.value == 7: # If TV mix is selected, wait 4 seconds
                    print("TV mix selected, waiting 4 seconds")
                    time.sleep(4)
            elif max(meters) > micLevelThreshold:
                active_mic = meters.index(max(meters)) # get index of mic with highest level (above threshold)
                if active_mic in leftMics and preview_id != 1:
                    print("Hearing noise in mic", int(active_mic)+1, "previewing camera 1")
                    ATEM.preview(1)
                elif active_mic in leftMics and preview_id == 1:
                    print("Still hearing noise in mic", int(active_mic)+1, "cutting to camera 1")
                    ATEM.program(1)
                if active_mic in rightMics and preview_id != 3:
                    print("Hearing noise in mic", int(active_mic)+1, "previewing camera 3")
                    ATEM.preview(3)
                elif active_mic in rightMics and preview_id == 3:
                    print("Still hearing noise in mic", int(active_mic)+1, "cutting to camera 1")
                    ATEM.program(3)
            else:
                if preview_id != 2:
                    print("No significant noise detected in any mics, previewing camera 2")
                    ATEM.preview(2)
                if preview_id == 2:
                    print("Still no significant noise detected in any mics, cutting to camera 2")
                    ATEM.program(2)