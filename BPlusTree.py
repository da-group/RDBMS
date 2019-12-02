


class Node(object):

  '''
  if the node is leaf node, values[i] is a list of index of keys[i]
  else, values[i] is a node containing keys less or equals keys[i] and larger than keys[i-1].
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


  def __getitem__(self, index):
    assert index<len(self.keys) and index>=0, "wrong index"
    return self.keys[index]


  def size(self):
    return len(self.keys)


  def addLeaf(self, key, value):
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


  def addNonLeaf(self, node, index):
    self.keys = self.keys[:index]+node.keys+self.keys[index+1:]
    self.values = self.values[:index]+node.values+self.values[index+1:]


  def split(self):
    left = Node(self.order)
    right = Node(self.order)
    mid = int(self.order/2)+1

    left.keys = self.keys[:mid]
    left.values = self.values[:mid]
    right.keys = self.keys[mid:]
    right.values = self.values[mid:]

    self.keys = [left.keys[-1]]
    self.values = [left, right]
    self.isLeaf = False


  def full(self):
    return len(self.keys)>=self.order



class BPlusTree(object):

  def __init__(self, order):
    self.order = order
    self.root = Node(self.order)


  def __str__(self):
    return str(self.root)


  def __searchNode(self, node, key):
    if node.isLeaf:
      return node
    # non-leaf node
    for i in range(node.size()):
      if key<=node[i]:
        return self.__searchNode(node.values[i], key)
      if i+1==node.size():
        return self.__searchNode(node.values[i+1], key)


  def search(self, key):
    # find the leaf node
    node = self.__searchNode(node, key)
    for i in range(node.size()):
      if key==node[i]:
        return node.values[i]
    return None


  def insert(self, key, value):
    # build search path
    stack = []
    cur = self.root
    while not cur.isLeaf:
      for i in range(cur.size()):
        if key<=cur[i]:
          stack.append((cur, i))
          break
        if i+1==cur.size():
          stack.append((cur, i+1))
          i = i+1
          break
      cur = cur.values[i]

    cur.addLeaf(key, value)
    if cur.full():
      cur.split()
      while len(stack)>0:
        parent, index = stack.pop()
        parent.addNonLeaf(cur, index)
        cur = parent
        if not cur.full():
          break
        cur.split()

    
  def delete(self, key, value):
    node = self.__searchNode(self.root, key)
    values = None
    index = None
    for i in range(node.size()):
      if key==node[i]:
        values = node.values[i]
        index = i
        break
    assert values, "key does not exist"
    assert value in values, "index does not exist"

    node.values[index].remove(value)



if __name__ == '__main__':
  t = BPlusTree(3)
  t.insert(1, 2)
  t.insert(3, 4)
  t.insert(0, 3)
  t.insert(4, 3)
  t.insert(6, 3)
  t.insert(7, 3)
  t.delete(7, 3)
  print(t)