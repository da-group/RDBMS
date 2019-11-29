import os
from Type import *


class Attribute(object):
  '''
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


  def addValue(self, v):
    '''
    First check value-type consistency.
    '''
    assert isinstance(v, TypeDict[self.type.value]), "wrong type of value!"
    self.__values.append(v)


  def deleteValue(self, index):
    '''
    index: integer
    '''
    self.value.remove(index)


  def updateValue(self, index, v):
    assert isinstance(v, TypeDict[self.type.value]), "wrong type of value!"
    assert index<len(self.__values)
    self.value[index] = v


  def getSize(self):
    return len(self.__values)
    




if __name__=='__main__':
    a = Attribute(name="a1", type=AttrTypes.INT, key=[AttrKeys.PRIMARY])
    a.addValue(1)
    print(a)
