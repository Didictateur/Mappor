import os.path
import imageio
import numpy as np
import matplotlib.pyplot as plt

from .pixel import *

class Tile:
    def __init__(self, size: int=16, Vmax: int=255, name: str="0"):
        """Creates a square of pixels

        Args:
            size (int, optional): Size of the edges of the tile. Defaults to 16.
            Vmax (int, optional): The maximum value of the pixel. Defaults to 255.
        """
        self.size = size
        self.Vmax = Vmax
        self.tiles = []
        for i in range(self.size):
            self.tiles.append([])
            for j in range(self.size):
                self.tiles[-1].append(Pixel(0, 0, 0, self.Vmax))
        self.name = name
        self.type = "Tile"
        
    def __eq__(self, __value) -> bool:
        if __value == None:
            return False
        for i in range(self.size):
            for j in range(self.size):
                if self.tiles[i][j] != __value.tiles[i][j]:
                    return False
        return True
    
    def __neq__(self, __value) -> bool:
        return not self == __value
        
    def copy(self) -> object:
        newTile = Tile(self.size, self.Vmax, self.name+"cp")
        for i in range(self.size):
            for j in range(self.size):
                newTile.tiles[i][j] = self.tiles[i][j].copy()
        return newTile
        
    #Body
    def setPixel(self, pos: tuple[int], color: list[int]) -> None:
        x, y = pos
        self.tiles[x][y] = Pixel(color[0], color[1], color[2], self.Vmax)
    
    def toImg(self) -> list[list[list[int]]]:
        img = []
        for i in range(self.size):
            img.append([])
            for j in range(self.size):
                img[-1].append(self.tiles[i][j].pixels)
        return img
    
    #Saves
    def save(self, path: str, format: str="mprt") -> None:
        if format == "mprt":
            savePath = path+"/"+self.name+".mprt"
            n = self.size
            with open(savePath, 'w') as f:
                f.write(f"{self.Vmax}\n")
                for i in range(n):
                    msg = ""
                    for j in range(n):
                        pix = self.tiles[i][j]
                        msg += f"p {pix.R} {pix.G} {pix.B} "
                    msg += '\n'
                    f.write(msg)
        elif format == 'png':
            img = np.array(self.toImg(), dtype=np.uint8)
            plt.imsave(path+"/"+self.name+".png", img)
        else:
            raise Exception(f"No known extension {format}")
        
    @staticmethod
    def load(fileName: str) -> object:
        Lname = fileName.split('.')
        tiles = []
        if Lname[-1] == "mprt":
            R, G, B = None, None, None
            with open(fileName, 'r') as f:
                for line in [line.split() for line in f.readlines() if line.split()!=[]]:
                    if line[0] != 'p':
                        Vmax = int(line[0])
                    else:
                        tiles.append([])
                        for v in line:
                            if v == "p":
                                if B != None:
                                    tiles[-1].append(Pixel(R, G, B, Vmax))
                                    R, G, B = None, None, None
                            elif R == None:
                                R = int(v)
                            elif G == None:
                                G = int(v)
                            elif B == None:
                                B = int(v)
                            else:
                                raise Exception("The file is corrupted")
                        if B != None:
                            tiles[-1].append(Pixel(R, G, B, Vmax))
                            R, G, B = None, None, None
        else:
            raise Exception(f"Unknown extension {Lname[-1]}")
        path = Lname[-2].split('/')
        name = path[-1]
        t = Tile(len(tiles), Vmax, name)
        t.tiles = tiles
        return t