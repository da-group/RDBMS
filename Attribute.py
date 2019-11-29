import os
from Type import *
from Condition import condition


class Attribute(object):

  '''
    self.name: str
    self.type: Element of AttrTypes
    self.key: list of Elements of AttrKeys
  '''

  def __init__(self, **args):
    self.name = args['name']
    self.type = args['type']
    self.key = args.get('key', [AttrKeys.NULL])
    self.__values = []

    #  key is also not null
    if not isinstance(self.key, list):
      self.key = [self.key]
    if len(self.key)==1 and self.key[0]==AttrKeys.PRIMARY:
      self.key.append(AttrKeys.NOT_NULL)

    assert not (AttrKeys.NOT_NULL in self.key and AttrKeys.NULL in self.key), "impossible combination"


  def __str__(self):
    res = "name: "+self.name+"\n" + \
          "type: "+str(self.type.value)+"\n" + \
          "key property: "+str([ele.value for ele in self.key])+"\n" + \
          "num of values: "+str(len(self.__values))
    return res


  def __getitem__(self, index):
    assert index<len(self.__values) and index>=0, "out of list bounding"
    return self.__values[index]


  def addValue(self, v):
    '''
    should check value-type consistency.
    '''
    if AttrKeys.NOT_NULL in self.key:
      assert v, "Not null key!"
      assert isinstance(v, TypeDict[self.type.value]), "wrong type of value!"
      self.__values.append(v)
    else:
      if v==None:
        self.__values.append(v)
      else:
        assert isinstance(v, TypeDict[self.type.value]), "wrong type of value!"
        self.__values.append(v)


  def deleteValue(self, index):
    '''
    index: integer or list
    '''
    if isinstance(index, int):
      index = [index]
    index = sorted(index, reverse=True)
    print(self.__values)
    print(index)
    for i in index:
      assert i<len(self.__values) and i>=0, "out of list bounding"
      self.__values.pop(i)


  def updateValue(self, index, v):
    '''
    index: integer
    '''
    assert isinstance(v, TypeDict[self.type.value]), "wrong type of value!"
    assert index<len(self.__values) and index>=0, "out of list bounding"
    self.__values[index] = v


  def getSize(self):
    return len(self.__values)


  def getIndexByCondition(self, condition):
    '''
    condition: function with arguments of attribute value
    return list of index satisfy the condition
    '''
    res = []
    for i in range(len(self.__values)):
      if self.__values[i] and (condition(self.__values[i])):
        res.append(i)
    return res


  def getAttributeByIndex(self, index):
    '''
    this method assumes index list does not contain duplicate elements
                        and the index list is in an ascending order
                        and the elements are no larger than len(self.__value)
    index: list of integers
    '''
    res = Attribute(name=self.name, type=self.type, key=self.key)
    for i in index:
      res.addValue(self.__values[i])
    return res
    


if __name__=='__main__':
    a = Attribute(name="a1", type=AttrTypes.INT, key=[AttrKeys.NULL])
    a.addValue(None)
    a.addValue(1)
    a.addValue(1)
    # a.updateValue(0, 2)
    # a.deleteValue([0, 1])
    c = condition('greater', 0)
    index = a.getIndexByCondition(c)
    print(index)
    a1 = a.getAttributeByIndex(index)
    print(a1[0])
