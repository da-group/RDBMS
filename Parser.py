import re
from Condition import condition


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
    if string!="":
      res.append(string)
  return res



def parseAction(string):
  pass



def parseFroms(statement):
  pass


def parseJoins(joins):
  pass



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


def __parseSingleCondition(statement):
  if '(' in statement:
    # there are only tow cases may contain parethesis: in and inside
    # delete the parethesis
    index = statement.find('(')
    statement = statement[:index]+statement[index+1:len(statement)-2]
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

  c = None
  if symbol=='in':
    target = []
    for ele in targets:
      if __isNumber(ele):
        target.append(float(ele))
      elif __isString(ele):
        target.append(ele[1:len(ele)-1])
    c = condition(symbol, target, ifNot)
  elif symbol=='inside':
    assert len(targets)==2, "wrong number of tokens in condition "+statement
    assert __isNumber(targets[0]) and __isNumber(targets[1]), "wrong format of range "+statement
    start = float(targets[0])
    end = float(targets[1])
    c = condition(symbol, (start, end), ifNot)
  elif symbol=='=' or symbol=='!=':
    assert len(targets)==1, "wrong number of tokens in condition "+statement
    target = targets[0]
    if __isNumber(target):
      target = float(target)
    elif __isString(target):
      target = target[1:len(target)-1]
    c = condition(symbol, target, ifNot)
  elif symbol=="like":
    assert len(targets)==1, "wrong number of tokens in condition "+statement
    target = targets[0]
    assert __isString(target), "wrong format of pattern "+statement
    target = target[1:len(target)-1]
    c = condition(symbol, target, ifNot)
  else:
    assert len(targets)==1, "wrong number of tokens in condition "+statement
    target = targets[0]
    assert __isNumber(target), "wrong format of number "+statement
    target = float(target)
    c = condition(symbol, target, ifNot)

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
  cnfStrs = statement.split("or")
  for cnfStr in cnfStrs:
    cnf = []
    conditions = cnfStr.split("and")
    for condition in conditions:
      cnf.append(__parseSingleCondition(condition))
    res.append(cnf)
  return res


############################## ###############################


def parseGroups(statement):
  pass


def parseHaving(statement):
  pass


def parseOrdered(statement):
  pass


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

  if "ordered by" in statement:
    action, ordered = statement.split("ordered by")
  else:
    action = statement

  if "having" in statement:
    action, having = statement.split("having")
  else:
    action = statement

  if "group by" in statement:
    action, groups = statement.split("group by")
  else:
    action = statement

  if "where" in statement:
    action, conditions = statement.split("where")
  else:
    action = statement

  if "join" in statement:
    split = statement.split("group by")
    assert len(split)>=2, "wrong format of join statement"
    action = split[0]
    for i in range(1, len(split)):
      joins.append(split[i])
  else:
    action = statement

  if "from" in statement:
    action, froms = statement.split("from")
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
  statement = "select c1 from t1 where not c1 inside (2.4, 4.5) and c2 in ('true', 'dfs') or c3 >= 3.4"
  res = parseCondition(statement.split("where")[1])
  print(res[0][0][1](3))
  print(res[0][1][1]("false"))
