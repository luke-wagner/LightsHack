import sys
import os

# Add the parent directory to the system path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from gameslib.GameObject import GameObject

class PlayerObj(GameObject):
    def __init__(self, _name, _sprite=None, _position=[0,0]):
        GameObject.__init__(self, _name, _sprite, _position)
    
    def detectCollisions(self, gameObjects):
        for gameObject in gameObjects:
            if gameObject == self:
                continue

            if (gameObject.position[0] == self.position[0] or gameObject.position[0] == self.position[0] + 1
                ) and (gameObject.position[1] == self.position[1] or gameObject.position[1] == self.position[1] + 1):
                return gameObject