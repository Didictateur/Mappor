from .draw import *
from .ground import *

class Map(Draw):
    def __init__(self, initSize: tuple[int], tileSize: int, Vmax: int=255, name: str="0"):
        super().__init__(initSize, tileSize, Vmax, name)
        self.ground = Ground(self.size)
        self.type = "Map"
        
    def addDraw(self, pos: tuple[int], draw: Draw) -> None:
        x, y = pos
        while x < 0:
            x += 1
            self.addLeft
        while y < 0:
            y += 1
            self.addUp
        for i in range(x + len(draw.draw)):
            for j in range(y + len(draw.draw[0])):
                self.setTile((i, j), draw.draw[i-x][j-y])
                
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
        g = Ground((len(gtiles), len(gtiles[0])))
        g.tiles = gtiles
        realTiles = []
        for i in range(n):
            realTiles.append([None]*m)
        for i in range(n):
            for j in range(m):
                realTiles[i][j] = tiles[m*i+j]
        m = Map((len(tiles), len(tiles[0])), tileSize, Vmax, name)
        m.draw = realTiles
        m.ground = g
        return m