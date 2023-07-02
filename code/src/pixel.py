class Pixel:
    def __init__(self, R: int, G: int, B: int, Vmax: int=255):
        """A pixel in RGB

        Args:
            R (int): red composante
            G (int): green composante
            B (int): blue composante
            Vmax (int, optional): Gives the maximum value of a pixel. Defaults to 255.
        """
        self.R = R
        self.G = G
        self.B = B
        self.pixels = [R, G, B]
        if len([x for x in self.pixels if x >= 0 and x <= Vmax]) != 3:
            raise Exception(f"Invalue values for a pixel: {self.R} {self.G} {self.B}")
        self.Vmax = Vmax
    
    def __eq__(self, __value) -> bool:
        return self.pixels == __value.pixels
    
    def __neq__(self, __value) -> bool:
        return not self == __value
        
    def copy(self) -> object:
        pix = Pixel(self.R, self.G, self.B)
        return pix