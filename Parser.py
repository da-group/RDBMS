import re
from datetime import datetime
from Condition import condition
from Attribute import *
from Table import *
from Database import *
from Statistic import *
from Type import *


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
    res = {}
    string = string.strip(";")
    #action = string.split(" ")
    if("select" in string):
        res["action_type"] = "select"
        string = string.split("select")[1]
        attrs = string.split(",")
        for i in range(len(attrs)):
            attrs[i] = attrs[i].strip()
        if(len(attrs)==1 and attrs[0] == "*"):
            attrs = "all"
        res["attrs"] = attrs
        
#        print(attrs)
    elif("insert" in string):
        res['action_type'] = "insert"
        string = string.split("insert ")[1].split("into ")[1]
        tablename = string.split(' ')[0].strip()
        res['tablename'] = tablename
        
        
        
        attr_val ={}
        
        temp = re.findall(r'\(.*?\)',string)
        if(len(temp)>1): 
            attrs = temp[0]
            values = temp[1]
            attrs = attrs.lstrip("(").rstrip(")").split(",")
            values = values.lstrip("(").rstrip(")").split(",")
            assert len(attrs) == len(values),"Wrong num of Values"
            for i in range(len(attrs)):
                attr_val[attrs[i].strip()] = values[i].strip().strip('\'')
                
        else:
            values = temp[0]
            values = values.lstrip("(").rstrip(")").split(",")
        
        res['attrs_values'] = attr_val
        
            
        for i in range(len(values)):
            values[i] = values[i].strip().strip('\'')
        

        #print(attrs)
#        print(values)
#        print("insert")
        
    elif("delete" in string):
        res["action_type"] = "delete"
#        tablename = string.split("delete from ")[1].strip()
#        res["tablename"] = tablename
#        print(tablename)
#        print("delete")
    elif("update" in string):
        res["action_type"] = "update"
        string = string.split("update ")[1].split("set ")
        tablename =string[0].strip()
        assignments = string[1].split(",")
        assignment_dist = {}
        for a in assignments:
            attr = a.split("=")[0].strip()
            value = a.split("=")[1].strip().strip('\'')
            assignment_dist[attr] = value
        res["tablename"] = tablename
        res["assignments"] = assignment_dist
#        print(tablename)
#        print(assignments)
#        print(assignment_dist)
#        
#        print("update" )
    elif("create table" in string):
        res["action_type"] = "create"
        string = string.split("create table ")[1]
        temp =re.findall(r'\(.*\)',string)[0]
        tablename = string.replace(temp,'').strip()
        ak = temp.lstrip("(").rstrip(")").split(",")
        primary =  ak[len(ak)-1].split("primary key")[1].lstrip("(").rstrip(")").strip()
        attr_list = []
        
        for a in ak:
            if("primary key" not in a):
                a= a.strip().split(" ")
                a_name = a[0]
                a_type = a[1]
                a_key = "NULL"
                if a_name == primary: a_key = AttrKeys.PRIMARY
                if(len(a)>2):
                    if a[2] =="not": a_key = AttrKeys.NOT_NULL   
                attr = Attribute(name=a_name, type=AttrTypes[a_type.upper()], key=a_key)
                attr_list.append(attr)
        res["tablename"] = tablename
        res["attrs"] = attr_list
#        print("create table")
    elif("drop table" in string):
        res["action_type"] = "drop"
        tablename = string.split("drop table ")[1].strip()
        res['tablename'] = tablename
#        print(tablename)
#        print("drop table")
    elif("alter table" in string):
        string = string.split("alter table ")[1].strip().split(" ")
        tablename = string[0].strip()
        res['tablename'] = tablename
        attr_name = string[2].strip()
        if "add" in string and len(string)==4:
            res["action_type"] = "alter add"
            attr_type = string[3].strip()
            attr = Attribute(name=attr_name, type=AttrTypes[attr_type.upper()])
            res["attr"] = attr
#            print("add")
        elif "drop" in string and len(string)==3:
            res["action_type"] = "alter drop"
            res['attr'] = attr_name
#            print("drop")
#        print(attr)
#        print(tablename)
#        print("alter table")
    elif("create index" in string):
#        print("create index")
    elif("drop index" in string):
#        print("drop index")
    else: print("CANNOT PARSE ACTIONS")
    
    
    return res


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
  field = tmp[1].strip()

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
    statement, ordered = statement.split(" ordered by ")
  else:
    statement = statement

  if " having " in statement:
    statement, having = statement.split(" having ")
  else:
    statement = statement

  if " group by " in statement:
    statement, groups = statement.split(" group by ")
  else:
    statement = statement

  if " where " in statement:
    statement, conditions = statement.split(" where ")
    print(conditions)
  else:
    statement = statement

  if " join " in statement:
    split = statement.split(" join ")
    assert len(split)>=2, "wrong format of join statement"
    statement = split[0]
    for i in range(1, len(split)):
      joins.append(split[i])
  else:
    statement = statement

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
  
  create = "CREATE TABLE Students(ROLL_NO int,NAME varchar NOT NULL,SUBJECT varchar, primary key(roll_No));"
  alter_1 = "ALTER TABLE students ADD gender varchar"
  alter_2 = "alter table students drop gender"
  drop = "drop table students"
  insert = "INSERT INTO Websites (name, url, country) VALUES ('stackoverflow'  , 'http://stackoverflow.com/', 'IND');"
  select_1 = "SELECT class_id, AVG(score)"
  select_2 = "select *"
  update = "UPDATE Person SET FirstName = 'Fred',LastName = 'Andromeda'"
  delete = "DELETE FROM Customers"
  parse = parse(insert)  
  print(parse)