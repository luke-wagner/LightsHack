class GameObject:
    def __init__(self, _name, _sprite=None, _position=[0,0]):
        self.name = _name
        self.sprite = _sprite
        self.position = _position
        self.zIndex = 0  # Default value