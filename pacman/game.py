import copy
import asyncio
from pynput import keyboard
from pynput.keyboard import Key
import random
from collections import deque

from gameslib.GameObject import *
from lightslib.LightsController import LightsController
from pacman.PlayerObj import PlayerObj
from pacman.sprites import *

GAME_WIDTH = 20
GAME_HEIGHT = 14

drawingFrame = False

# Dictionary to track which keys are currently pressed
keys_held = {}

frame = []
gameObjects = []

for i in range(GAME_WIDTH):
    column = ['  '] * GAME_HEIGHT
    frame.append(column)

lightsController = LightsController()
asyncio.run(lightsController.connect(run_simul_on_fail=True))

backgroundObj = GameObject("background", backgroundSprite)
gameObjects.append(backgroundObj)

playerObj = PlayerObj("player", playerSprite, [9,6])
gameObjects.append(playerObj)

pellets = [
    GameObject("pellet", pelletSprite, [1, 3]),
    GameObject("pellet", pelletSprite, [1, 6]),
    GameObject("pellet", pelletSprite, [1, 10]),
    GameObject("pellet", pelletSprite, [4, 1]),
    GameObject("pellet", pelletSprite, [4, 6]),
    GameObject("pellet", pelletSprite, [4, 12]),
    GameObject("pellet", pelletSprite, [9, 11]),
    GameObject("pellet", pelletSprite, [10, 2]),
    GameObject("pellet", pelletSprite, [14, 1]),
    GameObject("pellet", pelletSprite, [14, 12]),
    GameObject("pellet", pelletSprite, [15, 6]),
    GameObject("pellet", pelletSprite, [18, 3]),
    GameObject("pellet", pelletSprite, [18, 6]),
    GameObject("pellet", pelletSprite, [18, 10])
]

for pellet in pellets:
    gameObjects.append(pellet)

enemies = []

enemy1 = GameObject("enemy", enemySprite2, [17, 11])
enemy2 = GameObject("enemy", enemySprite1, [1, 1])

enemies.append(enemy1)
enemies.append(enemy2)
gameObjects.append(enemy1)
gameObjects.append(enemy2)

gameNotOver = True

def clearFrame():
    global frame
    
    for i in range(GAME_WIDTH):
        for j in range(GAME_HEIGHT):
            frame[i][j] = '  '

async def newFrame():
    global drawingFrame
    global frame

    drawingFrame = True

    clearFrame()

    # Sort the gameObjects list by zIndex so sprites are drawn in the correct order
    # Not sure if this will work
    gameObjects.sort(key=lambda obj: obj.zIndex)

    for object in gameObjects:
        drawGameObject(object)

    await lightsController.drawFrame(frame)

    drawingFrame = False

def drawGameObject(gameObject):
    if gameObject.sprite == None:
        print("ERROR: Draw function called on object with no sprite")
        return

    for i in range(gameObject.sprite.width):
        for j in range(gameObject.sprite.height):
            # Draw pixel
            coordX = i + gameObject.position[0] - gameObject.sprite.origin[0]
            coordY = j + gameObject.position[1] - gameObject.sprite.origin[1]
            ledNumber = coordX * 20 + coordY
            color = gameObject.sprite.pixelData[i][j]
            
            if coordX >= 0 and coordX < GAME_WIDTH and coordY >= 0 and coordY < GAME_HEIGHT:
                #print("Coloring (" + str(coordX) + ", " + str(coordY) + "), led number: " + str(ledNumber) + ", with " + color)
                frame[coordX][coordY] = color

# Check if a proposed position is valid for a gameObject based on its sprite size
# Return true if position is valid, else return false
def checkBounds(gameObject, position):
    # gameObject.sprite.origin decides where the sprite is centered at. This is a tuple of ints
    # gameObject.width and gameObject.height properties decide the size of the sprite in pixels (integer value)
    # emptyTiles is a python list of tuples, that symbolizes the free squares in the game grid. Any x-y value not in emptyTiles
    # should be assumed to be a wall, where the gameObject cannot go.
    # Function should return false if any part of the gameObject would be drawn over a wall (or non-empty tile)
    
    sprite_origin = gameObject.sprite.origin  # (x_offset, y_offset)
    sprite_width = gameObject.sprite.width
    sprite_height = gameObject.sprite.height
    
    # Calculate the top-left corner of the sprite based on the position and origin
    top_left_x = position[0] - sprite_origin[0]
    top_left_y = position[1] - sprite_origin[1]
    
    # Iterate over every pixel of the sprite and check if it's within emptyTiles
    for x in range(top_left_x, top_left_x + sprite_width):
        for y in range(top_left_y, top_left_y + sprite_height):
            if (x, y) not in emptyTiles:
                return False  # A part of the sprite is over a non-empty tile
    
    return True  # All parts of the sprite are within emptyTiles


def getEmptyTiles(sprite):
    """
    Convert the sprite's pixelData into a list of valid (x, y) tuples (emptyTiles).
    Only include positions with '  ' in the resulting list.
    """
    emptyTiles = []
    for x, col in enumerate(sprite.pixelData):
        for y, value in enumerate(col):
            if value == '  ':
                emptyTiles.append((x, y))
    return emptyTiles

emptyTiles = getEmptyTiles(backgroundSprite)

def getEnemyWalkableTiles():
    list_to_return = []

    for position in emptyTiles:
        if checkBounds(enemy1, position):
            list_to_return.append(position)
    
    return list_to_return

enemyWalkableTiles = getEnemyWalkableTiles()


def entityMovedEvent():
    global gameNotOver

    collisionObj = playerObj.detectCollisions(gameObjects)

    if collisionObj != None:
        if collisionObj.name == "pellet":
            gameObjects.remove(collisionObj)
        elif collisionObj.name == "enemy":
            if playerObj in gameObjects:
                gameObjects.remove(playerObj)
            gameNotOver = False

    newFrame()

async def tryMovePlayer():
    print("Moving player...")
    currentPos = playerObj.position

    if keys_held.get(Key.up, False) and checkBounds(playerObj, (currentPos[0],currentPos[1] - 1)):
        print("Up held")
        playerObj.position[1] -= 1
        entityMovedEvent()
    elif keys_held.get(Key.down, False) and checkBounds(playerObj, (currentPos[0],currentPos[1] + 1)):
        print("Down held")
        playerObj.position[1] += 1
        entityMovedEvent()
    elif keys_held.get(Key.right, False) and checkBounds(playerObj, (currentPos[0] + 1,currentPos[1])):
        print("Right held")
        playerObj.position[0] += 1
        entityMovedEvent()
    elif keys_held.get(Key.left, False) and checkBounds(playerObj, (currentPos[0] - 1,currentPos[1])):
        print("Left held")
        playerObj.position[0] -= 1
        entityMovedEvent()

def tryMoveEnemy(enemy):
    print("moving enemy...")

    if enemy.position == playerObj.position:
        return True

    def findPath(start, goal, validTiles):
        """Find the shortest path from start to goal using BFS."""
        queue = deque([start])
        came_from = {start: None}  # To reconstruct the path
        directions = [(1, 0), (-1, 0), (0, 1), (0, -1)]  # Right, Left, Down, Up

        while queue:
            current = queue.popleft()
            if current == goal:
                break
            
            for d in directions:
                neighbor = (current[0] + d[0], current[1] + d[1])
                if neighbor in validTiles and neighbor not in came_from:
                    queue.append(neighbor)
                    came_from[neighbor] = current

        # Reconstruct the path
        path = []
        current = goal
        while current and current != start:
            path.append(current)
            current = came_from.get(current)
        
        return path[::-1]  # Return the path from start to goal

    currentPos = tuple(enemy.position)  # Ensure it's a tuple
    playerPos = tuple(playerObj.position)  # Ensure it's a tuple
    
    # Convert enemyWalkableTiles to a set of tuples
    validTiles = {tuple(tile) for tile in enemyWalkableTiles}
    
    # Find the path from the enemy to the player
    path = findPath(currentPos, playerPos, validTiles)
    
    # If there's a path, move the enemy one step closer to the player
    if path:
        nextStep = path[0]  # First step in the path
        if nextStep in validTiles:  # Ensure the step is valid
            enemy.position = list(nextStep)  # Convert back to a list if needed
            return True
    
    return False  # No valid move found

    '''
    if index == 0:
        if enemy.position[index] + value >= 0 and enemy.position[index] + value < GAME_WIDTH:
            enemy.position[index] += value
            return True
        else:
            return False
    else:
        if enemy.position[index] + value >= 0 and enemy.position[index] + value < GAME_HEIGHT:
            enemy.position[index] += value
            return True
        else:
            return False
    '''

async def moveEnemies():
    global enemies

    for enemy in enemies:
        moved = False

        while moved == False:
            if random.random() > 0.5:
                index = 1
            else:
                index = 0

            if random.random() > 0.5:
                moved = tryMoveEnemy(enemy)
            else:
                moved = tryMoveEnemy(enemy)
    
    entityMovedEvent()
        

def on_press(key):
    try:
        keys_held[key.char] = True
        #print("Key press")
    except AttributeError:
        keys_held[key] = True
        #print("Key press")

def on_release(key):
    try:
        keys_held[key.char] = False
        print("Key released")
    except AttributeError:
        keys_held[key] = False
        print("Key released")

async def check_exit_condition():
    if keys_held.get('q', False):
        print("Exiting...")

        # Disconnect from the lights
        await lightsController.disconnect()

        quit()

# Start keyboard listener
listener = keyboard.Listener(on_press=on_press, on_release=on_release)
listener.start()

async def main():
    global gameNotOver
    global gameObjects
    global playerObj

    await lightsController.drawBlankFrame()

    while True:
        await newFrame()

        while gameNotOver:
            print("new Frame...")
            start_time = asyncio.get_event_loop().time()  # Get the current time
            await check_exit_condition()
            await moveEnemies()
            await tryMovePlayer()
            await newFrame()
            
            # Calculate the time taken for this loop iteration
            elapsed_time = asyncio.get_event_loop().time() - start_time
            frame_duration = 1 / 2  # Target duration for 3 frames per second (0.3333 seconds)
            
            # Sleep for the remaining time if the loop was faster than the frame duration
            if elapsed_time < frame_duration:
                await asyncio.sleep(frame_duration - elapsed_time)

        # Reset game
        print("resetting...")
        playerObj = PlayerObj("player", playerSprite, [9,6])
        gameObjects.append(playerObj)

        enemy1.position = (17, 11)
        enemy2.position = (1, 1)

        gameNotOver = True
        await asyncio.sleep(2)


asyncio.run(main())