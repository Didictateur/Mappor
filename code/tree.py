import os

class Tree:
  def __init__(self, root_path: str=None):
    self.root_path = root_path
    self.absolutePath = ""
    self.pathFromRoot = ""

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
    
