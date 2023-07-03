class Ground:
    def __init__(self, initSize: tuple[int], name: str='0'):
        """
        Posiible cases:
            0 to 9: stepable floor
            B: block
            S: shadder to change the floor
            W: water
            V: void
            I: ice
            T: teleporter
            D: door
            N: one step to the north
            S: one step to the south
            W: one step to the west
            E: one step to the east
        """
        self.size = initSize
        self.tiles = []
        n, m = self.size
        for i in range(n):
            self.tiles.append(['0']*m)
        self.name = name
        self.type = "Ground"
        
        
    #Body
    
    
    #Saves
    def save(self, path: str, format: str="mprg") -> None:
        if format == "mprg":
            savePath = path+"/"+self.name+".mprg"
            with open(savePath, 'w') as f:
                n, m = self.size
                for i in range(n):
                    for j in range(m):
                        f.write(f"{self.tiles[i][j]} ")
                    f.write('\n')
        else:
            raise Exception(f"No known extension {format}")
        
    @staticmethod
    def load(fileName: str) -> object:
        Lname = fileName.split('.')
        if Lname[-1] == "mprg":
            tiles = []
            with open(fileName, 'r') as f:
                for line in [line.split() for line in f.readlines() if line.split()!=[]]:
                    tiles.append(line)
        else:
            raise Exception(f"Unknown extension {Lname[-1]}")
        path = Lname[-1].split('/')
        name = path[0]
        g = Ground((len(tiles), len(tiles[0])))
        g.tiles = tiles
        return g