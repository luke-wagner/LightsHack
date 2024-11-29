class Sprite:
    def __init__(self, _width, _height):
        self.width = _width
        self.height = _height
        self.origin = [0,0] # Default, anchor sprite position at top left
        self.pixelData = [] # Start with an empty list

        for i in range(_width):
            column = ['  '] * _height
            self.pixelData.append(column)