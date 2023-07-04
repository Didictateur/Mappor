from .tile import *

class Draw:
    def __init__(self, initSize: tuple[int], tileSize: int, Vmax: int=255, name: str="0"):
        self.draw: list[list[(None | Tile)]] = []
        self.size = initSize
        n, m = self.size
        for i in range(n):
            self.draw.append([None]*m) #None is considered as transparent
        self.tileSize = tileSize
        self.Vmax = Vmax
        self.name = name
        self.type = "Draw"
        
    def __eq__(self, __value) -> bool:
        if __value == None:
            return False
        n, m = self.size
        for i in range(n):
            for j in range(m):
                if self.draw[i][j] != __value.draw[i][j]:
                    return False
        return True
    
    def __neq__(self, __value) -> bool:
        return not self == __value
        
    def toImg(self) -> list[list[list[int]]]:
        """Returns the draw has an image that can be drawn"""
        n, m = self.size
        img = []
        for i in range(n*self.tileSize):
            img.append([])
            for j in range(m*self.tileSize):
                img[-1].append([0, 0, 0])
        for i in range(n):
            for j in range(m):
                for x in range(self.tileSize):
                    for y in range(self.tileSize):
                        tile = self.draw[i][j]
                        if tile != None:
                            img[i*self.tileSize+x][j*self.tileSize+y] = [int(255*value/self.Vmax) for value in tile.tiles[x][y].pixels]
                        else:
                            if (x+y)%2 == 0:
                                img[i*self.tileSize+x][j*self.tileSize+y] = [100, 100, 100]
                            else:
                                img[i*self.tileSize+x][j*self.tileSize+y] = [200, 200, 200]
        return img
    
    def copy(self) -> object:
        newDraw = Draw(self.size, self.tileSize, self.Vmax, self.name)
        n, m = self.size
        for i in range(n):
            for j in range(m):
                if self.draw[i][j] == None:
                    newDraw.draw[i][j] = None
                else:
                    newDraw.draw[i][j] = self.draw[i][j].copy()
        return newDraw
    
    #Body
    def addRight(self) -> None:
        n, m = self.size
        self.size = (n, m+1)
        self.draw = [ldraw+[None] for ldraw in self.draw]
        
    def addLeft(self) -> None:
        n, m = self.size
        self.size = (n, m+1)
        self.draw = [[None]+ldraw for ldraw in self.draw]
        
    def addUp(self) -> None:
        n, m = self.size
        self.size = (n+1, m)
        self.draw = [[None]*m] + self.draw
        
    def addDown(self) -> None:
        n, m = self.size
        self.size = (n+1, m)
        self.draw.append([None]*m)
        
    def removeRight(self) -> None:
        n, m = self.size
        self.size = (n, m-1)
        self.draw = [ldraw[:-1] for ldraw in self.draw]
        
    def removeLeft(self) -> None:
        n, m = self.size
        self.size = (n, m-1)
        self.draw = [ldraw[1:] for ldraw in self.draw]
        
    def removeUp(self) -> None:
        n, m = self.size
        self.size = (n-1, m)
        self.draw = self.draw[1:]
        
    def removeDown(self) -> None:
        n, m = self.size
        self.size = (n-1, m)
        self.draw = self.draw[:-1]
    
    def setTile(self, pos: tuple[int], tile: Tile) -> None:
        x, y = pos
        n, m = self.size
        while x < 0:
            x += 1
            self.addLeft()
        while x > n-1:
            n += 1
            self.addRight()
        while y < 0:
            y += 1
            self.addUp()
        while y > m-1:
            m += 1
            self.addDown()
        if tile == None:
            self.draw[x][y] = None
        else:
            self.draw[x][y] = tile.copy()
        
    def setPixel(self, pos: tuple[int], color: list[int]) -> None:
        x, y = pos
        n = self.tileSize
        tile = self.draw[x//n][y//n]
        if tile != None:
            tile.setPixel((x%n, y%n), color)
        else:
            tile = Tile(self.tileSize, self.Vmax)
            tile.setPixel((x%n, y%n), color)
            self.draw[x//n][y//n] = tile
            
    def resize(self) -> None:
        while [d for d in self.draw[0] if d != None] == [] and len(self.draw) > 1: #up
            self.removeUp()
        while [d for d in self.draw[-1] if d != None] == [] and len(self.draw) > 1: #down
            self.removeDown()
        while [l[0] for l in self.draw if l[0] != None] == [] and len(self.draw[0]) > 1: #left
            self.removeLeft()
        while [l[-1] for l in self.draw if l[-1] != None] == [] and len(self.draw[0]) > 1: #right
            self.removeRight()
    
    #Saves
    def save(self, path: str, format: str="mprd") -> None:
        if format == "mprd":
            savePath = str(path)+"/"+self.name+".mprd"
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
        elif format == "png":
            img = np.array(self.toImg(), dtype=np.uint8)
            plt.imsave(path+"/"+self.name+".png", img)
        else:
            raise Exception(f"No known extension {format}")
        
    @staticmethod
    def load(fileName: str) -> object:
        Lname = fileName.split('.')
        if Lname[-1] == "mprd":
            R, G, B = None, None, None
            tiles = []
            with open(fileName, 'r') as f:
                for line in [line.split() for line in f.readlines() if line.split()!=[]]:
                    pixels = []
                    if line[0] == "param":
                        tileSize, Vmax, n, m = int(line[1]), int(line[2]), int(line[3]), int(line[4])
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
            raise Exception(f"Unknown extension {Lname[-1]}")
        path = Lname[-2].split('/')
        name = path[-1]
        realTiles = []
        for i in range(n):
            realTiles.append([None]*m)
        for i in range(n):
            for j in range(m):
                realTiles[i][j] = tiles[m*i+j]
        d = Draw((n, m), tileSize, Vmax, name)
        d.draw = realTiles
        return d