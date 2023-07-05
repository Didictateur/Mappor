# Mappor

Mappor is a 2D-map creator. It allows you to to designe and custom your project, from a little house to a whole new world.

## Hierarchy of the map

A 2D-map is made of small cases in wich the player can move. Thoses cases are the fundamental element in order to construct the entire world.
More precisely, the visual data a a case is a Tile. Then, those Tile can be combined to create Draw, wich can be use to create Map

### Tile

A Tile is juste a square of pixel. It can be designed, saved and change. For example, here some Tile for a house:

![Door1](/home/decosse/Bureau/Mappor/img/Door_Top.png)

![Door2](/home/decosse/Bureau/Mappor/img/Door_Bottom.png)

![Window](/home/decosse/Bureau/Mappor/img/Window.png)

A Tile is necessarely complete, and the default pixel is black.

### Draw

Combining different Tile together make a Draw. This is useful to create an object wich can be reused as a tree, a store, a path, or even a house:

![House](/home/decosse/Bureau/Mappor/img/House.png)

Event if the Tile are the same, rearranging them differently make them feel differently.

![house](/home/decosse/Bureau/Mappor/img/house.png)

The default value of a Tile for a Draw is None. It means these Tile is transparent, represented by an alternating gray pixels

![bg](/home/decosse/Bureau/Mappor/img/bg.png)

### Map

A Map is a special type of Draw. It is the combination of Tile and Draw.
- The Draw can be used to rapidely generate a forest, a city and so on...
- While the Tile allows us to change the details

Moreover, a Map also contain a Ground.

### Ground

A Ground is a type of data contained by a Map. It tells to the game what type of case the map contains. By default, a case is setted to 0. The value can be:
- int between 0 and 9 : Steppable case. The number tells the floor, and the player can't directly change floor
- B : A block. The player can't go thought it
- S : Stairs or Ladder. Steppable case which link between all floor
- W : Water
- V : Void
- I : Ice or Slide. The player can't controle the movement and slide to the end
- T : Teleporter
- D : Door
- N : North one-step case. This allows the player to only move one step to the north
- S : Suth one-step case
- W : Western one-step
- E : Eastern one-step