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
          for f in res["foreign_key"]:
              assert len(f)==4,"Wrong foreign key"
              self.database.addForeignKey(f[0].strip(','),f[1].strip(','),f[2].strip(','),f[3].strip(','))

       
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
      tables = res['froms']
      attrs = res['attrs']
      conditions = res['conditions']
      results = []
      op = ""
      
      
      
      

      for t in tables:
          assert t in self.database.tables.keys(), "No such table"
          a_list = []
          c_list = []
          for a in attrs:
              if(re.fullmatch(r'.{3}\(.*\)',a) or re.fullmatch(r'.{5}\(.*\)',a)):
                  assert len(attrs)==1,"invalid nums of attributes"
                  attr =re.findall(r'[(](.*?)[)]',a)[0].strip()
                  a_list.append(attr)
                  op = a.replace(re.findall(r'\(.*?\)',a)[0],'')
                  
              elif(a in t.attributes.keys()):
                  a_list.append(a)
              elif a == "*":
                  a_list = t.attributes.keys()
              elif('.' in a):
                  if(a.split('.')[0] == t and a.split(".")[1] in t.attributes.keys()):
                      a_list.append(a.split(".")[1])
                      
                  
          for c in conditions:
              if(c[0] == t) :
                  c_list.append(c)
          result=t.select(a_list,c_list)
          
          if(op == ""):results.append(result)
          else:
              attr = result.getAttribute(a_list[0])
              results.append(FuncMap[op](attr))
              
       
        
      print(results)
      
      
      
      
      
      
      
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
