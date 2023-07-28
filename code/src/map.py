from .draw import *
from .ground import *

class Map(Draw):
    def __init__(self, initSize: tuple[int], tileSize: int, Vmax: int=255, name: str="0"):
        super().__init__(initSize, tileSize, Vmax, name)
        self.ground = Ground(self.size)
        self.type = "Map"
        
    def __eq__(self, __value: object) -> bool:
        if __value == None:
            return False
        return self.draw==__value.draw and self.ground==__value.ground
        
    def addDraw(self, pos: tuple[int], draw: Draw) -> None:
        x, y = pos
        n, m = draw.size
        n_, m_ = self.size
        for i in range(n):
            for j in range(m):
                if draw.draw[i][j] is not None and x+i in range(n_) and y+j in range(m_):
                    self.setTile((x+i, y+j), draw.draw[i][j])
                
    def save(self, path: str, format: str="mprp") -> None:
        if format == "mprp":
            savePath = str(path)+"/"+self.name+".mprp"
            with open(savePath, 'w') as f:
                n, m = self.size
                f.write(f"param {self.tileSize} {self.Vmax} {n} {m}\n")
                
                for i in range(len(self.draw)):
                    for j in range(len(self.draw[0])):
                        f.write("t ")
                        tile = self.draw[i][j]
                        if tile != None:
                            for x in range(self.tileSize):
                                for y in range(self.tileSize):
                                    pix = tile.tiles[x][y]
                                    f.write(f"p {pix.R} {pix.G} {pix.B} ")
                            f.write('\n')
                        else:
                            f.write("N\n")
                
                f.write(f"ceiling\n")
                for i in range(len(self.draw)):
                    for j in range(len(self.draw[0])):
                        f.write("t ")
                        tile = self.draw[i][j]
                        if tile != None:
                            for x in range(self.tileSize):
                                for y in range(self.tileSize):
                                    f.write(f"{int(tile.ceiling[y][x])} ")
                            f.write('\n')
                        else:
                            f.write("N\n")
                
                f.write("ground\n")
                for i in range(n):
                    for j in range(m):
                        f.write(f"{self.ground.tiles[i][j]} ")
                    f.write('\n')
        elif format == "png":
            img = np.array(self.toImg(), dtype=np.uint8)
            plt.imsave(path+"/"+self.name+".png", img)
        else:
            raise Exception(f"No known extension {format}")
        
    @staticmethod
    def load(fileName: str) -> object:
        Lname = fileName.split('.')
        if Lname[-1] == "mprp":
            R, G, B = None, None, None
            tiles = []
            gtiles = []
            with open(fileName, 'r') as f:
                is_ground = False
                for line in [line.split() for line in f.readlines() if line.split()!=[]]:
                    if not is_ground:
                        pixels = []
                        if line[0] == "param":
                            tileSize, Vmax, n, m = int(line[1]), int(line[2]), int(line[3]), int(line[4])
                        elif line[0] == "ground":
                            is_ground = True
                        elif line[1] == "N":
                            tiles.append(None)
                        else:
                            R, G, B = None, None, None
                            for v in line[1:]:
                                if v == 'p':
                                    if B != None:
                                        pixels.append(Pixel(R, G, B, Vmax))
                                        R, G, B = None, None, None
                                else:
                                    if R == None:
                                        R = int(v)
                                    elif G == None:
                                        G = int(v)
                                    elif B == None:
                                        B = int(v)
                                    else:
                                        raise Exception("The file is corrupted")
                            if B != None:
                                pixels.append(Pixel(R, G, B, Vmax))
                            tile = Tile(tileSize, Vmax)
                            for i in range(tileSize):
                                for j in range(tileSize):
                                    tile.tiles[i][j] = pixels[i*tileSize+j]
                            tiles.append(tile)
                    else:
                        gtiles.append(line)
        else:
            raise Exception(f"Unknown extension {Lname[-1]}")
        path = Lname[-2].split('/')
        name = path[-1]
        g = Ground((n, m))
        g.tiles = gtiles
        realTiles = []
        for i in range(n):
            realTiles.append([None]*m)
        for i in range(n):
            for j in range(m):
                realTiles[i][j] = tiles[m*i+j]
        map_ = Map((n, m), tileSize, Vmax, name)
        map_.draw = realTiles
        map_.ground = g
        return map_
    
    def copy(self) -> None:
        newMap = Map(self.size, self.tileSize, self.Vmax, self.name)
        newMap.draw = []
        n, m = self.size
        for i in range(n):
            newMap.draw.append([])
            for j in range(m):
                if self.draw[i][j] == None:
                    newMap.draw[-1].append(None)
                else:
                    newMap.draw[-1].append(self.draw[i][j].copy())
        newMap.ground.tiles = []
        for i in range(n):
            newMap.ground.tiles.append([])
            for j in range(m):
                newMap.ground.tiles[-1].append(self.ground.tiles[i][j])
        return newMap
    
    # Body
    def addRight(self) -> None:
        n, m = self.size
        self.size = (n, m+1)
        self.draw = [ldraw+[None] for ldraw in self.draw]
        self.ground.tiles = [ltiles+["0"] for ltiles in self.ground.tiles]
        
    def addLeft(self) -> None:
        n, m = self.size
        self.size = (n, m+1)
        self.draw = [[None]+ldraw for ldraw in self.draw]
        self.ground.tiles = [["0"]+ltiles for ltiles in self.ground.tiles]
        
    def addUp(self) -> None:
        n, m = self.size
        self.size = (n+1, m)
        self.draw = [[None]*m] + self.draw
        self.ground.tiles = [["0"]*m]+self.ground.tiles
        
    def addDown(self) -> None:
        n, m = self.size
        self.size = (n+1, m)
        self.draw.append([None]*m)
        self.ground.tiles.append(["0"]*m)
        
    def removeRight(self) -> None:
        n, m = self.size
        self.size = (n, m-1)
        self.draw = [ldraw[:-1] for ldraw in self.draw]
        self.ground.tiles = [ltile[:-1] for ltile in self.ground.tiles]
        
    def removeLeft(self) -> None:
        n, m = self.size
        self.size = (n, m-1)
        self.draw = [ldraw[1:] for ldraw in self.draw]
        self.ground.tiles = [ltile[1:] for ltile in self.ground.tiles]
        
    def removeUp(self) -> None:
        n, m = self.size
        self.size = (n-1, m)
        self.draw = self.draw[1:]
        self.ground.tiles = self.ground.tiles[1:]
        
    def removeDown(self) -> None:
        n, m = self.size
        self.size = (n-1, m)
        self.draw = self.draw[:-1]
        self.ground.tiles = self.ground.tiles[:-1]