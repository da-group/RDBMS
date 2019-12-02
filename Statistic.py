from Attribute import Attribute
from Type import *
from collections import Counter

FuncMap = {
  'sum': __sum,
  'avg': __avg,
  'min': __min,
  'max': __max,
  'count': __count,
}


def __sum(attr: Attribute):
  assert attr.type in [AttrTypes.INT, AttrTypes.FLOAT], "wrong attribute type"
  res = 0
  for i in range(attr.getSize()):
    res += attr[i]
  return res


def __avg(attr):
  assert attr.type in [AttrTypes.INT, AttrTypes.FLOAT], "wrong attribute type"
  res = 0
  for i in range(attr.getSize()):
    res += attr[i]
  return res/attr.getSize()


def __min(attr):
  assert attr.type in [AttrTypes.INT, AttrTypes.FLOAT, AttrTypes.DATE], "wrong attribute type"
  res = attr[0]
  for i in range(attr.getSize()):
    res = min(res, attr[i])
  return res


def __max(attr):
  assert attr.type in [AttrTypes.INT, AttrTypes.FLOAT, AttrTypes.DATE], "wrong attribute type"
  res = attr[0]
  for i in range(attr.getSize()):
    res = max(res, attr[i])
  return res


def __count(attr):
  counter = Counter()
  for i in range(attr.getSize()):
    counter[attr[i]] += 1
  return len(counter)