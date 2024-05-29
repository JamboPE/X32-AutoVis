import PyATEMMax
import time
import env

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
        if camera_id != preview_id:
            switcher.setPreviewInputVideoSource(0, camera_id)  # Preview camera_id on ME1
            preview_id = camera_id
    def program(camera_id):
        if camera_id != program_id:
            switcher.setProgramInputVideoSource(0, camera_id)  # Program camera_id on ME1
            program_id = camera_id

def check_mics():
    return None

if __name__ == "__main__":
    print("Connecting to ATEM switcher...")
    ATEM.connect(env.atem_ip)
    print("Connected to ATEM switcher")
    print("Setting Program and Preview to Camera 2")
    ATEM.preview(2)
    ATEM.program(2)

    print("Starting AutoVis loop")

    if env.YSTV_Live:
        while True:
            print("Checking if VT is playing (checking for mute group 1)...")
            while False: # need to impiment checking for X32 mute group 1 using OSC
                print("A VT is playing: setting VT to program, previewing wide")
                ATEM.preview(2)
                time.sleep(0.1) # trying not to spam atem and X32 with too many requests
            if switcher.programInput[0].videoSource.value == 7: # If TV mix is selected, wait 4 seconds
                print("TV mix selected, waiting",env.tv_mix_time,"seconds")
                time.sleep(env.tv_mix_time)
                print("Cutting away from TV mix")
            check_mics()
            time.sleep(env.cut_timeout)
    
    if not env.YSTV_Live:
        while True:
            check_mics()
            time.sleep(env.cut_timeout)