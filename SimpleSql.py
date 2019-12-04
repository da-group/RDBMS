import os
import traceback
from Parser import parseCondition
from Parser import parse
from Database import *
from Table import *
from datetime import datetime
from Statistic import *
import re

class SimpleSql(object):
  '''
  our datebase management system
  '''

  def __init__(self):
    # to be implemented
    self.path = './data/'
    self.database = None


 
  def _load_database(self, name):
    '''
    load from self.path
    '''
    path = self.path+name+".db"
    
    with open(path,"rb") as f:
        self.database = pickle.load(f)
    self._show()



  def _save_database(self):
      assert self.database != None,"NO DATABASE!"
      path = self.path+self.database.name+".db"
      self.database.saveToFile(path)

 
 
  
  def _create(self,res):
      self.database.createTable(res['tablename'],res['attrs'])
      
      if("foreign_key") in res.keys():
#          print(res["foreign_key"])
          for f in res["foreign_key"]:
              assert len(f)==5,"Wrong foreign key"
              self.database.addForeignKey(f[0],f[1],f[2],f[3],f[4])

       
      self._save_database()
      


      
      
      
  def _alter(self,res):
      if(res["action_type"] == "alter add"):
          table = self.database.getTableByName(res['tablename'])
          table.addAttribute(res['attr'])
      elif(res["action_type"] == "alter drop"):
          table = self.database.getTableByName(res['tablename'])
          table.deleteAttribute(res['attr'])
      self.save_database()
  def _drop(self, res):
      self.database.dropTable(res['tablename'])
      self._save_database()



  def _select(self, res):
      print(res)
      tables = res['froms']
      attrs = res['attrs']
      if 'conditions' in res.keys(): conditions = res['conditions']
      else: conditions = None
      if 'join' in res.keys(): joins = res['join']
      else: joins = []
      if 'groups' in res.keys(): groups = res['groups']
      else: groups = None
      if 'having' in res.keys(): having = res['having']
      else: having = None
      if 'order' in res.keys(): order = res['ordered']
      else: order = None
      results = []
      op = "" 

      tc_dict = {}
      for join in joins:
          tc1, _, tc2 = join
          t1, c1 = tc1.split(".")
          t2, c2 = tc2.split(".")
          if t1 not in tc_dict.keys():
              tc_dict[t1] = []
          if t2 not in tc_dict.keys():
              tc_dict[t2] = []
          if c1 not in tc_dict[t1]:
              tc_dict[t1].append(c1)
          if c2 not in tc_dict[t2]:
              tc_dict[t2].append(c2)


      for t in tables:
          assert t in self.database.tables.keys(), "No such table"
          t = self.database.getTableByName(t)
          a_list = []
          c_list = []
          for a in attrs:
              if(re.fullmatch(r'.{3}\(.*\)',a) or re.fullmatch(r'.{5}\(.*\)',a)):
                  assert len(attrs)==1,"invalid nums of attributes"
                  attr =re.findall(r'[(](.*?)[)]',a)[0].strip()
                  a_list.append(attr)
                  op = a.replace(re.findall(r'\(.*?\)',a)[0],'')
                  
              elif a in t.attributes.keys():
                  a_list.append(a)
              elif a == "all":
                  a_list = t.attributes.keys()
              elif('.' in a):
                  if(a.split('.')[0] == t.name and a.split(".")[1] in t.attributes.keys()):
                      a_list.append(a.split(".")[1])
          
          if len(tc_dict)!=0:
              for a in tc_dict[t.name]:
                  if a not in a_list:
                      a_list.append(a)    
                  
          c_list = conditions

          print(a_list)
          result=t.select(a_list,c_list,"temp-"+t.name)
          self.database.addTable(result)
          
          if(op == ""):
              results.append(result)
          else:
              attr = result.getAttribute(a_list[0])
              results.append(FuncMap[op](attr))

      m = {}
      for join in joins:
          tc1, symbol, tc2 = join
          t1, c1 = tc1.split(".")
          t2, c2 = tc2.split(".")
          while t1 in m.keys():
              t1 = m[t1]
          while t2 in m.keys():
              t2 = m[t2]
          if not t1.startswith("temp-"): nt1 = "temp-"+t1+"."+c1
          else: nt1 = t1+"."+c1
          if not t2.startswith("temp-"): nt2 = "temp-"+t2+"."+c2
          else: nt2 = t2+"."+c2
          res = self.database.join([(nt1, symbol, nt2)], "temp-"+nt1+nt2)
          self.database.addTable(res)
          m[t1] = res.name
          m[t2] = res.name

      # if join, we assume there is only one table
      if len(m)!=0:
          t1 = tables[0]
          ret = None
          while t1 in m.keys():
              t1 = m[t1]
          t1 = self.database.getTableByName(t1)
          if attrs[0] == 'all':
              a_list = t1.attributes.keys()
          else:
              a_list = [ele.split(".")[-1] for ele in attrs]
          print(a_list)
          ret = t1.project(a_list)
          if op=="":
              print(ret)
          else:
              attr = ret.getAttribute(attrs[0].split(".")[-1])
              print(FuncMap[op](attr))

      else: 
          print("aaa")
          for r in results:
              print(r)

      toDelete = []
      for t in self.database.tables.keys():
          if t.startswith("temp-"):
              toDelete.append(t)
      for tname in toDelete:
          self.database.dropTable(tname)
   
      
      
      
      
  def _insert(self, res):
      table = self.database.getTableByName(res['tablename'])
#      print(table.attributes.keys())
#      print(res['attrs_values'].keys())
      for key in res['attrs_values'].keys():
          a_type = table.attributes[key].getType().lower()
          
          if(a_type == "int"):
              res['attrs_values'][key] = int(res['attrs_values'][key])
          elif(a_type == "float"):
              res['attrs_values'][key] = float(res['attrs_values'][key])
          elif(a_type == "date"):
              res['attrs_values'][key] = datetime.strptime(res['attrs_values'][key])
        
      table.addTuple(res['attrs_values'])
      print(table)
      self._save_database()
      
  def _update(self,res):
      table = self.database.getTableByName(res['tablename'])
      conditions = res['conditions']
      row = res['assignments']
      table.update(conditions, row)
      print(table)
      self._save_database()
  
  def _delete(self, res):
    table = self.database.getTableByName(res['froms'][0])
    if('conditions' in res.keys()):
        conditions = res['conditions']
        table.delete(conditions)
    else: table.delete()
    self._save_database()
    print(table)
    
    
  def _createdb(self,name):
      
     if(self.database!= None): self._save_database()
     self.database = Database(name)
      
      
  def _show(self):
    print(self.database)


  def _showtable(self):
      for k in self.database.tables.keys():
          print(self.database.tables[k])

  def _createindex(self,res):
      table = self.database.getTableByName(res['tablename'])
      attr = table.getAttribute(res['attr'])
      attr.buildIndex(10)
      self._save_database()
      
      



  def _exit(self):
    print("exit success!")
    exit(0)

  
  def run(self):
    while True:
      statement = input('SimpleSql> ')
#      print(statement)
      if(statement.lower().strip() == "exit"): break
      try:
          if(statement.lower().strip() == "show"):
              self._show()
              continue
          if(statement.lower().strip() == "show table"):
              self._showtable()
              continue
          
          res = parse(statement)
          if(res["action_type"] == "create"):
              assert self.database != None,"NO DATABASE!"
              self._create(res)
          elif(res["action_type"] == "drop"):
              assert self.database != None,"NO DATABASE!"
              self._drop(res)
          elif("alter" in res["action_type"]):
              assert self.database != None,"NO DATABASE!"
              self._alter(res)
          elif(res["action_type"] == "select"):
              assert self.database != None,"NO DATABASE!"
              self._select(res)
          elif(res["action_type"] == "insert"):
              assert self.database != None,"NO DATABASE!"
              self._insert(res)
          elif(res["action_type"] == "update"):
              assert self.database != None,"NO DATABASE!"
              self._update(res)
          elif(res["action_type"] == "delete"):
              assert self.database != None,"NO DATABASE!"
              self._delete(res)
          elif(res["action_type"] == "create index"):
              assert self.database != None,"NO DATABASE!"
              self._createindex(res)
              
          elif(res["action_type"] == "create db"):
              self._createdb(res["database_name"])
              self._show()
          elif(res["action_type"] == "load db"):
              self._load_database(res["database_name"])
#              self._show()  
      except:
            print(traceback.format_exc())
        #print(res)
 


if __name__ == '__main__':
  engine = SimpleSql()
  engine.run()
