
def standardize(strings):
  res = []
  for string in strings:
    if string!="":
      res.append(string)
  return res


def parseAction(string):
  strings = standardize(string.split(" "))


def parseCondition(string):
  '''
  input: a string after "where"
  output: return a 3-layer dictionary: or dict, and dict, condition dict
  condition dict: key is table.attribute, value is function
  '''
  pass


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
