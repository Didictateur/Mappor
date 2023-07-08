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
    
    if self.root_path != None:
      Lpath = root_path.split('/')
      self.name = Lpath[-1]
      self.absolutePath = self.root_path
      self.folder = os.path.isdir(self.absolutePath)
      for file in os.listdir(self.absolutePath):
        self.child.append(Tree.initChild(self, file))
  
  def __eq__(self, tree: object) -> bool:
    return self.absolutePath == tree.absolutePath

  def __neq__(self, tree: object) -> bool:
    return not self==tree
  
  def __le__(self, tree: object) -> bool:
    return self.absolutePath <= tree.absolutePath
  
  def __ge__(self, tree: object) -> bool:
    return self.absolutePath >= tree.absolutePath
  
  def __lt__(self, tree: object) -> bool:
    return self.absolutePath < tree.absolutePath
  
  def __gt__(self, tree: object) -> bool:
    return self.absolutePath > tree.absolutePath
  
  def list(self) -> list:
    L = [self]
    for child in self.child:
      L += child.list()
    return L
  
  def copyInfo(self, tree: object) -> None:
    """Only copy the information of the topest. The second object is calqued to the first one"""
    self.root_path = tree.root_path
    self.pathFromRoot = tree.pathFromRoot
    self.name = tree.name
    self.folder = tree.folder
    self.expanded = tree.expanded
    
  def changeExpanded(self, pathFromRoot) -> None:
    lpath = [path for path in pathFromRoot.split('/') if path != '']
    if len(lapath) == 1:
      if self.name == lpath[0]:
        self.expanded = not self.expanded
      elif self.folder:
        l = [file for file in self.child if file.name == lpath[0]]
        if len(l) == 1:
          l[0].expanded = not l[0].expanded
    l = [child for child in self.child if child.name == lpath[0]]
    if len(l) == 1:
      l[0].changeExpanded('/'.join(lpath[1:]))
    
  def pop(self, pathFromRoot) -> (None | object):
    lpath = [path for path in pathFromRoot.split('/') if path != '']
    if len(lpath) == 2 and lpath[0] == self.name:
      keepl = [child for child in self.child if child.name != lpath[1]]
      notkeepl = [child for child in self.child if child.name == lpath[1]]
      if len(notkeepl) == 1:
        self.child = keepl
        return keepl[0]
      return None
    l = [child for child in self.child if child.name == lpath[1]]
    if len(l) == 1:
      return l[0].pop('/'.join(lpath[1:]))
    
  def append(self, tree, pathFromRoot) -> None:
    lpath = [path for path in pathFromRoot.split('/') if path != '']
    if len(lapath) == 1:
      if not tree.name in [t.name for t in self.child]:
        self.child.append(tree)
    l = [child for child in self.child if child.name == lpath[0]]
    if len(l) == 1:
      l[0].append(tree, '/'.join(lpath[1:]))
    
  @staticmethod
  def initChild(parentTree, fileName) -> object:
    tree = Tree()
    tree.root_path = parentTree.root_path
    tree.pathFromRoot = parentTree.pathFromRoot + '/' +fileName
    tree.absolutePath = tree.root_path+tree.pathFromRoot
    tree.name = fileName
    tree.folder = os.path.isdir(tree.absolutePath)
    if tree.folder:
      for file in os.listdir(tree.absolutePath):
        tree.child.append(Tree.initChild(tree, file))
    return tree
    
  @staticmethod
  def fuse(t1: object, t2: object) -> None:
    """If the is similarity, apply t1 to t2, then don't returns the new t2"""
    if t1.absolutePath == t2.absolutePath:
      t2.copyInfo(t1)
      commonChild, t1child, t2child = intersection(t1.child, t2.child)
      t1.child = sorted(t1.child)
      t2.child = sorted(t2.child)
      i1 = 0
      i2 = 0
      while i1 < len(commonChild):
        if t1.child[i1] in commonChild:
          if t2.child[i2] not in commonChild:
              i2 += 1
          else:
            Tree.fuse(t1.child[i1], t2.child[i2])
            i1 += 1
            i2 += 1
        else:
          i1 += 1
    
  @staticmethod
  def merge(t1: object, t2: object) -> None:
    """If the is similarity, apply t1 to t2, then don't returns the new t2, even in the middle"""
    if t1.absolutePath != t2.absolutePath:
      if t1 in t2.list():
        for child in t2.child:
          if t1 in child.list():
            Tree.merge(t1, child)
      elif t2 in t1.list():
        for child in t1.child:
          if t2 in child.list():
            Tree.merge(child, t2)
    else:
      Tree.fuse(t1, t2)

def intersection(L1, L2):
  """returns :
    the intersection
    the surplus of L1
    the surplus of L2
  """
  Inter = []
  l1 = L1.copy()
  lr1 = []
  while l1:
    x = l1.pop()
    if x in L2:
      Inter.append(x)
    else:
      lr1.append(x)
  lr2 = [x for x in L2 if not x in Inter]
  return Inter, lr1, lr2

if __name__=="__main__":
  tree = Tree("/home/decosse/Bureau/saves")
  otherTree = Tree("/home/decosse/Bureau/saves/tile")
  print(tree.pop("saves/tile").name)