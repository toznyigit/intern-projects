class Link:
    def __init__(self, name, type, peer=None) -> None:
        self.name = name
        self.type = type
        self.peer = peer
        self.state = 0
        self.address = None

    def __get_state(self):
        if self.state: return "UP"
        else: return "DOWN"
        
    def __repr__(self) -> str:
        return f'name:{self.name}, peer:{self.peer}, type:{self.type}, status:{self.__get_state()}, address:{self.address}\n'
    