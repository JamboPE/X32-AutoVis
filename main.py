import PyATEMMax
from pythonosc import udp_client

atem_ip = "144.32.210.2"
X32_ip =  "144.32.210.3"
leftMics = [0,1] # zero infexed lol
rightMics = [2,3] # zero infexed lol
threshold = 0

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
        client.send_message(address, args)

if __name__ == "__main__":
    ATEM.connect(atem_ip)
    ATEM.preview(1)
    ATEM.program(1)
    while True:
        while send_osc_command(X32_ip, 10023, "/config/mute/1") == "OFF" and switcher.programInput[0].videoSource.value != 7: # Only runs autovis if a VT isn't playing (detected based on X32 mute group being on) and the TV mix isn't slected
            meters = []
            meters.append(send_osc_command(X32_ip, 10023, "/meters/6 0")) # get levels of mic 1
            meters.append(send_osc_command(X32_ip, 10023, "/meters/6 1")) # get levels of mic 2
            meters.append(send_osc_command(X32_ip, 10023, "/meters/6 2")) # get levels of mic 3
            meters.append(send_osc_command(X32_ip, 10023, "/meters/6 3")) # get levels of mic 4
            if max(meters) > threshold:
                active_mic = meters.index(max(meters)) # get index of mic with highest level (above threshold)
                if active_mic in leftMics and preview_id != 1:
                    ATEM.preview(1)
                elif active_mic in leftMics and preview_id == 1:
                    ATEM.program(1)
                if active_mic in rightMics and preview_id != 3:
                    ATEM.preview(3)
                elif active_mic in rightMics and preview_id == 3:
                    ATEM.program(3)
            else:
                if preview_id != 2:
                    ATEM.preview(2)
                if preview_id == 2:
                    ATEM.program(2)