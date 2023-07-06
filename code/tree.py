import os

class Tree:
  def __init__(self, root_path: str=None):
    self.root_path = root_path
    self.absolutePath = ""
    self.pathFromRoot = ""
    #we assule that root-path+pathFromRoot=absolutePath

    self.name = ""
    self.folder = True
    self.expanded = False

    self.child = []

  def copyInfo(self, tree: object) -> None:
    """Only copy the information of the topest"""
    self.root_path = tree.root_path
    self.pathFromRoot = tree.pathFromRoot
    self.name = tree.name
    self.folder = tree.folder
    self.expanded = tree.expanded

  @staticmethod
  def merge(t1: object, t2: object) -> object:
    """If the is similarity, apply t1 to t2, then returs the new t2"""
    if t1.absolutePath != t2.absolutePath:
      return t2



def intersection(L1, L2):
  """returns :
    the intersection
    the surplus of L1
    the surplus of L2"""
  Inter = []
  l1 = L1.copy()
  l1p = []
  while l1:
    x = l1.pop()
    if x in L2:
      Inter.append(x)
    else:
      l1p.append(x)
  l2p = []
