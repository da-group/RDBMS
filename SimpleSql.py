import os
from Parser import parseCondition

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


  def _select(self, *args):
    pass


  def _project(self, *args):
    pass


  def _show(self, *args):
    pass


  def _insert(self, *args):
    pass


  def _drop(self, *args):
    '''
    drop columns
    '''
    pass


  def _delete(self, *args):
    '''
    drop row
    '''
    pass


  def _exit(self):
    print("exit success!")
    exit(0)

  
  def run(self):
    while True:
      statement = input('SimpleSql> ')
      try:
        conditions = parseCondition(statement)
        print(conditions)
        pass
      except Exception as e:
        print("SimpleSql> "+str(e))



if __name__ == '__main__':
  engine = SimpleSql()
  engine.run()
