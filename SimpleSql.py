import os
from Parser import parseCondition
from Parser import parse
from Database import *
from Table import *


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
    pass

 
  
  def _create(self,res):
      self.database.createTable(res['tablename'],res['attrs'])         
      
      
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
      pass
  def _insert(self, res):
      table = self.database.getTableByName(res['tablename'])
      print(res['attrs_values'])
      table.addTuple(res['attrs_values'])
      
      
      
  def _update(self,res):
      pass
  
  def _delete(self, res):
    pass


  def _show(self, res):
    pass


  


  



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
      print(self.database)
        #print(res)
 


if __name__ == '__main__':
  engine = SimpleSql()
  engine.run()
