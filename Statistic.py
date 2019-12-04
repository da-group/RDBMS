from Attribute import Attribute
from Type import *
from collections import Counter




def sumOp(attr: Attribute):
  assert attr.type in [AttrTypes.INT, AttrTypes.FLOAT], "wrong attribute type"
  res = 0
  for i in range(attr.getSize()):
    res += attr[i]
  return res


def avgOp(attr):
  assert attr.type in [AttrTypes.INT, AttrTypes.FLOAT], "wrong attribute type"
  res = 0
  for i in range(attr.getSize()):
    res += attr[i]
  return res/attr.getSize()


def minOp(attr):
  assert attr.type in [AttrTypes.INT, AttrTypes.FLOAT, AttrTypes.DATE], "wrong attribute type"
  res = attr[0]
  for i in range(attr.getSize()):
    res = min(res, attr[i])
  return res


def maxOp(attr):
  assert attr.type in [AttrTypes.INT, AttrTypes.FLOAT, AttrTypes.DATE], "wrong attribute type"
  res = attr[0]
  for i in range(attr.getSize()):
    res = max(res, attr[i])
  return res


def countOp(attr):
  return attr.getSize()



FuncMap = {
  'sum': sumOp,
  'avg': avgOp,
  'min': minOp,
  'max': maxOp,
  'count': countOp,
}