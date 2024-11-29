import asyncio
from bleak import BleakClient
import time

from config import *

class LightsController:
    def __init__(self):
        self.address = BD_ADDR
        self.client = BleakClient(self.address)
        self.connected = False
        asyncio.run(self.connect())

    # Establish connection to the lights
    async def connect(self):
        try:
            await self.client.connect()
            print("Connection successful...")
            self.connected = True
        except:
            print("Unable to connect to lights. Continuing program execution...")
            self.connected = False

    # Disconnect from the lights
    async def disconnect(self):
        await self.client.disconnect()

    # Draws new frame with reference to the old frame, draws each pixel individually
    async def drawFramePartial(self, currentFrame, previousFrame):
        difference = self.__computeDifference(currentFrame, previousFrame)
        tasks = []

        width = len(difference)
        height = len(difference[0])

        start_time = time.time()

        for i in range(width):
            for j in range(height):
                if difference[i][j] != '  ':
                    numLed = i * 20 + j
                    tasks.append(self.__drawPixelSingle(numLed, difference[i][j]))

        await asyncio.gather(*tasks)

        end_time = time.time()
        elapsed_time = end_time - start_time
        print(f"Write time: {elapsed_time:.4f} seconds")


    # Draws completely new frame, each bulb is re-initialized. Uses L2CAP procedures
    def drawFrameComplete(self, frame):
        return
    
    async def drawBlankFrame(self):
        await self.__sendWriteCommand("aad00400646403bb")
        
    # Get the difference between the two matrices, return the new matrix
    def __computeDifference(self, currentFrame, previousFrame):
        difference = []     # this will be a matrix

        width = len(currentFrame)
        height = len(currentFrame[0])

        for i in range(width):
            newCol = []

            for j in range(height):
                currentVal = currentFrame[i][j]
                previousVal = previousFrame[i][j]

                if currentVal != previousVal:
                    if currentVal == '  ' and previousVal != '  ':
                        newCol.append('FE')
                    else:
                        newCol.append(currentVal)
                else:
                    newCol.append('  ')
            
            difference.append(newCol)
        
        return difference
    
    # Draw the specified color at led # = numLed
    async def __drawPixelSingle(self, numLed, color):
        numValueHex = hex(numLed)[2:].zfill(3)

        # craft hex code
        hexCode = "aad1030" + numValueHex
        hexCode += color + "bb"

        # Send write command to lights
        await self.__sendWriteCommand(hexCode)

    async def __sendWriteCommand(self, hexCode):
        # This is the uuid of the device to write to
        characteristic_uuid = CHAR_UUID

        # Don't try writing if not connected to the lights
        if self.connected == False:
            return

        try:
            await self.client.write_gatt_char(characteristic_uuid, bytes.fromhex(hexCode), response=False)
        except:
            print("Error sending write command. Continuing program execution...")
