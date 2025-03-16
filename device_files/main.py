import machine
import time
import uasyncio as asyncio
import gc

from lightslib.LightsController import LightsController
from espinput.input import *

gc.enable()

# Send a blank frame to turn all lights off
# -- Don't attach a LEDController for this function, not needed
async def power_off():
    lightsController = LightsController()
    
    # Try connecting until successful
    successful = await lightsController.connect()
    while successful == False:
        print("Failed to connect to lights. Retrying...")
        successful = await lightsController.connect()

    # Turn off the lights
    await lightsController.drawBlankFrame()

    # Disconnect so that other code can use the lights
    if lightsController.connected:
        await lightsController.disconnect()

# Code that will run on boot
# -- Start by connecting to the lights and ensuring they are off
async def startup():
    await power_off()

async def main():
    await startup()

    while True:
        print("Waiting for power on signal...")
        
        while True:
            # Wait for power on signal
            # Add btn1 event while btn0 is disconnected -- REMOVE LATER
            if btn0_event[1].is_set() or btn1_event[1].is_set():
                print("Power on signal received")
                btn0_event[1].clear()
                btn1_event[1].clear()
                break
                
            time.sleep(0.2)
            
        print("Waiting for user to start game...")
        
        while True:
            # Wait for select button press (right button)
            if button_pressed(4):
                break
            
            time.sleep(0.1)

        # Run the game
        print("Starting game...")
        print("Memory allocated: " + str(gc.mem_alloc()))
        print("Free memory: " + str(gc.mem_free()))
        try:
            execfile("pacman/game.py")
        except SystemExit:
            # Don't exit the main program if game.py exits early
            pass

        if btn0_event[1].is_set():
            print("Power off received after game end")
            machine.reset()
        
        gc.collect()
        print("\nMemory allocated: " + str(gc.mem_alloc()))
        print("Free memory: " + str(gc.mem_free()))
        time.sleep(2)

asyncio.run(main())