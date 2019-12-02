


class Node(object):

  '''
  if the node is leaf node, values[i] is a list of index of keys[i]
  else, values[i] is a node containing keys less and equals keys[i] and larger than keys[i-1]
  '''

  def __init__(self, order):
    self.order = order
    self.keys = []
    self.values = []
    self.isLeaf = True


  def __str__(self):
    res = ""
    for key in self.keys:
      res += str(key)+" "
    res += "\n"
    for value in self.values:
      if isinstance(value, list):
        res += str(value)+" "
      elif isinstance(value, Node):
        res += str(value)+"\n"
    return res


  def add(self, key, value):
    assert self.isLeaf, "connot insert key-value pair to non-leaf node"
    
    if len(self.keys)==0:
      self.keys.append(key)
      self.values = [[value]]
      return

    for i in range(len(self.keys)):
      pivot = self.keys[i]
      if pivot==key:
        assert value not in self.values[i], "cannot insert duplicate index"
        self.values[i].append(value)
        break
      elif key<pivot:
        self.keys = self.keys[:i] + [key] + self.keys[i:]
        self.values = self.values[:i] + [[value]] + self.values[i:]
        break
      if i+1==len(self.keys):
        self.keys += [key]
        self.values += [[value]]
        break


  def split(self):
    left = Node(self.order)
    right = Node(self.order)
    mid = self.order/2

    left.keys = self.keys[:mid]
    left.values = self.values[:mid]
    right.keys = self.keys[mid:]
    right.values = self.values[mid:]

    self.keys = [left.keys[-1]]
    self.values = [left, right]
    self.isLeaf = False



class BPlusTree(object):

  def __init__(self, order):
    self.order = order
    self.root = Node(self.order)

  def search(self, key):
    pass



if __name__ == '__main__':
  n = Node(6)
  n.add(1, 2)
  n.add(3, 4)
  n.add(0, 3)
  n.add(4, 3)
  n.add(6, 3)
  n.split()
  print(n)
