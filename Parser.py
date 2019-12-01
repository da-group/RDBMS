
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


def __parseSingleCondition(statement):
  tokens = standardize(statement.strip().split(" "))
  assert len(tokens)>=3, "wrong number of tokens in condition "+statement

  ifNot = False
  if tokens[0]=="not":
    ifNot = True
  pass



def parseCondition(statement):
  '''
  input: a string after "where"
  output: return a 2-layer lists: or list, and list whose elements are condition dict
  condition dict: key is table.attribute, value is function
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


def parse(statement):
  '''
  '''
  statement = statement.lower().strip()

  action = None
  conditions = None
  if "where" in statement:
    action, conditions = statement.split("where")
  else:
    action = statement

  res = parseAction(action)

  if conditions:
    res['conditions'] = parseCondition(conditions)

  return res


if __name__ == '__main__':
  statement = "select c1 from t1"
