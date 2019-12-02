import re
from datetime import datetime
from Condition import condition

from Statistic import *


SYMBOL_DICT = {
  '=': "equal",
  '!=': "not_equal",
  'in': "in",
  'inside': "inside",
  '>': "greater",
  '<': "smaller",
  '>=': "greater_equal",
  '<=': "smaller_equal",
  'like': "like"
}


def standardize(strings):
  res = []
  for string in strings:
    if string!="" and string!=",":
      res.append(string)
  return res



def parseAction(string):
  pass



def parseFroms(statement):
  '''
  return a list of table names
  '''
  tables = standardize(statement.split(","))
  for i in range(len(tables)):
    tables[i] = tables[i].strip()
  return tables



def parseJoins(joins):
  '''
  return a list of list
  list: (table1.column1, table2.column2)
  '''
  res = []
  for join in joins:
    _, columns = join.split(" on ")
    l = standardize(columns.split("="))
    for i in range(len(l)):
      l[i] = l[i].strip()
    assert len(l)==2, "wrong format of joins "+join
    res.append(l)
  return res



######################## methods used for condition parsing ##############################
def __isNumber(num):
  pattern = re.compile(r'^[-+]?[-0-9]\d*\.\d*|[-+]?\.?[0-9]\d*$')
  result = pattern.match(num)
  if result:
    return True
  else:
    return False

def __isString(s):
  return s.startswith("\'") and s.endswith("\'") or s.startswith("\"") and s.endswith("\"")

def __isDate(s):
  date = s.split("/")
  if len(date)==3 and len(date[0])==2 and len(date[1])==2 and len(date[2])==4 \
    and date[0].isdigit() and date[1].isdigit() and date[2].isdigit() \
    and int(date[0])>=1 and int(date[0])<=12 and int(date[1])>=1 and int(date[1])<=31:
    return True
  return False

def __convertToDate(s):
  return datetime.strptime(s, "%m/%d/%Y")


def __parseConditionTuple(symbol, targets, ifNot):
  c = None
  if symbol=='in':
    target = []
    for ele in targets:
      if __isNumber(ele):
        target.append(float(ele))
      elif __isDate(ele):
        target.append(__convertToDate(ele))
      elif __isString(ele):
        target.append(ele[1:len(ele)-1])
    c = condition(SYMBOL_DICT[symbol], target, ifNot)
  elif symbol=='inside':
    assert len(targets)==2, "wrong number of tokens in condition "+statement
    if __isDate(targets[0]) and __isDate(targets[1]):
      start = __convertToDate(targets[0])
      end = __convertToDate(targets[1])
    else:
      assert __isNumber(targets[0]) and __isNumber(targets[1]), "wrong format of range "+statement
      start = float(targets[0])
      end = float(targets[1])
    c = condition(SYMBOL_DICT[symbol], (start, end), ifNot)
  elif symbol=='=' or symbol=='!=':
    assert len(targets)==1, "wrong number of tokens in condition "+statement
    target = targets[0]
    if __isNumber(target):
      target = float(target)
    elif __isDate(target):
      target = __convertToDate(target)
    elif __isString(target):
      target = target[1:len(target)-1]
    c = condition(SYMBOL_DICT[symbol], target, ifNot)
  elif symbol=="like":
    assert len(targets)==1, "wrong number of tokens in condition "+statement
    target = targets[0]
    assert __isString(target), "wrong format of pattern "+statement
    target = target[1:len(target)-1]
    c = condition(SYMBOL_DICT[symbol], target, ifNot)
  else:
    assert len(targets)==1, "wrong number of tokens in condition "+statement
    target = targets[0]
    assert __isNumber(target) or __isDate(target), "wrong format of number "+statement
    if __isNumber(target):
      target = float(target)
    elif __isDate(target):
      target = __convertToDate(target)
    c = condition(SYMBOL_DICT[symbol], target, ifNot)
  return c


def __parseSingleCondition(statement):
  statement = statement.strip()
  if '(' in statement:
    # there are only tow cases may contain parethesis: in and inside
    # delete the parethesis
    index = statement.find('(')
    statement = statement[:index]+statement[index+1:len(statement)-1]
  tokens = standardize(statement.strip().split(" "))
  assert len(tokens)>=3, "wrong number of tokens in condition "+statement

  ifNot = False
  if tokens[0]=="not":
    ifNot = True
    tokens = tokens[1:]

  field = tokens[0]
  symbol = tokens[1]
  targets = tokens[2:]

  for i in range(len(targets)):
    if targets[i].endswith(","):
      targets[i] = targets[i][:-1]

  c = __parseConditionTuple(symbol, targets, ifNot)

  res = (field, c)
  return res
    

def parseCondition(statement):
  '''
  input: a string after "where"
  output: return a 3-layer lists: or list, and list whose elements are condition tuple
  condition tuple: (table.attribute, condition function)
  We assume that this statement does not contain "()".
  '''
  res = []
  cnfStrs = statement.split(" or ")
  for cnfStr in cnfStrs:
    cnf = []
    conditions = cnfStr.split(" and ")
    for condition in conditions:
      cnf.append(__parseSingleCondition(condition))
    res.append(cnf)
  return res

############################## ###############################



def parseGroups(statement):
  '''
  return a list of column names
  '''
  groups = standardize(statement.split(","))
  for i in range(len(groups)):
    groups[i] = groups[i].strip()
  return groups



############################## parse having conditions ###############################
def __parseSingleHaving(statement):
  '''
  return tuple: (column name, statistic function, condition function)
  '''
  l = standardize(statement.split(' '))
  assert len(l)>=3, "wrong format of having statement"
  for i in range(len(l)):
    if l[i].startswith("("):
      l[i] = l[i][1:len(l[i])]
    if l[i].endswith(")"):
      l[i] = l[i][:-1]
    if l[i].endswith(","):
      l[i] = l[i][:-1]
  
  ifNot = False
  if l[0]=="not":
    ifNot = True
    l = l[1:]
  
  stat = l[0]
  symbol = l[1]
  targets = l[2:]

  tmp = stat.split("(")
  assert len(tmp)==2, "wrong format of having statement"
  statFunc = FuncMap[tmp[0].strip()]
  field = tmp[1].strip()[:-1]

  c = __parseConditionTuple(symbol, targets, ifNot)
  res = (field, statFunc, c)
  return res



def parseHaving(statement):
  '''
  return result is similar to results from parseCondition's
  except the condition is represented as 3-element tuple (column name, statistic function, condition function)
  '''
  res = []
  cnfStrs = statement.split(" or ")
  for cnfStr in cnfStrs:
    cnf = []
    conditions = cnfStr.split(" and ")
    for condition in conditions:
      cnf.append(__parseSingleHaving(condition))
    res.append(cnf)
  return res


############################## ###############################




def parseOrdered(statement):
  '''
  return a list of tuples.
  tuple: (column name, isAscending)
  '''
  statements = statement.split(",")
  res = []
  for s in statements:
    s = s.strip()
    l = standardize(s.split(" "))
    assert len(l)==1 or len(l)==2, "wrong format of order "+statement
    if len(l)==2:
      assert l[1] in ['asc', 'desc'], "wrong format of order "+statement
    isAsc = True
    if l[1]=="desc":
      isAsc = False
    res.append((l[0], isAsc))
  return res


def parse(statement):
  '''
  '''
  statement = statement.lower().strip()

  action = None
  conditions = None
  groups = None
  ordered = None
  joins = []
  having = None
  froms = None

  if " ordered by " in statement:
    action, ordered = statement.split(" ordered by ")
  else:
    action = statement

  if " having " in statement:
    action, having = statement.split(" having ")
  else:
    action = statement

  if " group by " in statement:
    action, groups = statement.split(" group by ")
  else:
    action = statement

  if " where " in statement:
    action, conditions = statement.split(" where ")
  else:
    action = statement

  if " join " in statement:
    split = statement.split(" join ")
    assert len(split)>=2, "wrong format of join statement"
    action = split[0]
    for i in range(1, len(split)):
      joins.append(split[i])
  else:
    action = statement

  if " from " in statement:
    action, froms = statement.split(" from ")
  else:
    action = statement

  res = parseAction(action)

  if froms:
    res['froms'] = parseFroms(froms)

  if len(joins)>0:
    res['join'] = parseJoins(joins)

  if conditions:
    res['conditions'] = parseCondition(conditions)

  if groups:
    res['groups'] = parseGroups(groups)

  if having:
    res['having'] = parseHaving(having)

  if ordered:
    res['ordered'] = parseOrdered(ordered)

  return res


if __name__ == '__main__':
  statement = "select c1 from t1 where not c1 inside (2.4, 4.5) and c2 in ('true', 'dfs') or c3 >= 3.4 and c4 inside (03/04/2018, 04/05/2019)"
  res = parseCondition(statement.split("where")[1])
  print(res[0][0][1](3))
  print(res[0][1][1]("false"))
  print(res[1][1][1](datetime.strptime("07/20/2018", "%m/%d/%Y")))

  statement = "t1, t2, t3"
  print(parseFroms(statement))

  statement = "t1, t2 on t1.c2 = t2.c4"
  print(parseJoins([statement]))

  statement = "c1, c2,c3"
  print(parseGroups(statement))

  statement = "t1.c2 asc, t2.c3 desc"
  print(parseOrdered(statement))

  statement = "sum(t1.c2) >= 2 and max(t2.c3) inside (2.3, 4.3)"
  print(parseHaving(statement))
