from code.viewer import *

import matplotlib
matplotlib.use('TkAgg')
import matplotlib.pyplot as plt

t0 = Tile.load("./saves/tile/0.mprt")
t1 = Tile.load("./saves/tile/1.mprt")

fig, ax = plt.subplots()
img0 = np.array(t0.toImg(), dtype=np.uint8)
img1 = np.array(t1.toImg(), dtype=np.uint8)
ax.imshow(img0)
