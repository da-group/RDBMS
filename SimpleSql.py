import os
import traceback
from Parser import parseCondition
from Parser import parse
from Database import *
from Table import *
from datetime import datetime


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
    directory = self.path+name
    pass


  def _load_from_file(self, filename):
    pass


  def _save_database(self, path):
       self.database.saveToFile(path)

 
  
  def _create(self,res):
      self.database.createTable(res['tablename'],res['attrs'])
      if("foreign_key") in res.keys():
          for f in res["foreign_key"]:
              assert len(f)==4,"Wrong foreign key"
              self.database.addForeignKey(f[0],f[1],f[2],f[3])
      
      
  def _alter(self,res):
      if(res["action_type"] == "alter add"):
          table = self.database.getTableByName(res['tablename'])
          table.addAttribute(res['attr'])
      elif(res["action_type"] == "alter drop"):
          table = self.database.getTableByName(res['tablename'])
          table.deleteAttribute(res['attr'])
      
  def _drop(self, res):
      self.database.dropTable(res['tablename'])
      
      
  def _select(self, res):
      tables = res['froms']
      attrs = res['attrs']
      conditions = res['conditions']
      
      table_condition = {}
      table_attrs = {}
      
      #without aggregate operations
      for t in tables:
          assert t in self.database.tables.keys(), "No such table"
          a_list = []
          for a in attrs:
              if(a in t.attributes.keys()):
                  a_list.append(a)
              elif a == "*":
                  a_list = t.attributes.keys()
                  
          table_attrs[table.name] = a_list
      
      
      
      
      
      
      
      
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
      
      
  def _update(self,res):
      table = self.database.getTableByName(res['tablename'])
      conditions = res['conditions']
      row = res['assignments']
      table.update(conditions, row)
      print(table)
  
  def _delete(self, res):
    table = self.database.getTableByName(res['froms'][0])
    if('conditions' in res.keys()):
        conditions = res['conditions']
        table.delete(conditions)
    else: table.delete()
    
    print(table)
    
  def _show(self):
    print(self.database)





  def _exit(self):
    print("exit success!")
    exit(0)

  
  def run(self):
    self.database = Database("db1") 
    print(self.database)
    while True:
      statement = input('SimpleSql> ')
#      print(statement)
      if(statement.lower().strip() == "exit"): break
      try:
          if(statement.lower().strip() == "show"):
              self._show()
              continue
          res = parse(statement)
          if(res["action_type"] == "create"):
              self._create(res)
          elif(res["action_type"] == "drop"):
              self._drop(res)
          elif("alter" in res["action_type"]):
              self._alter(res)
          elif(res["action_type"] == "select"):
              self._select(res)
          elif(res["action_type"] == "insert"):
              self._insert(res)
          elif(res["action_type"] == "update"):
              self._update(res)
          elif(res["action_type"] == "delete"):
                self._delete(res)
      except:
            print(traceback.format_exc())
        #print(res)
 


if __name__ == '__main__':
  engine = SimpleSql()
  engine.run()
