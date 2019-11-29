class SimpleSql(object):
  '''
  our datebase management system
  '''

  def __int__(self):
    # to be implemented
    pass

  def run(self):
    while True:
      statement = input('SimpleSql> ')
      try:
        print(statement)
        pass
      except Exception as e:
        print("SimpleSql> "+str(e))



if __name__ == '__main__':
  engine = SimpleSql()
  engine.run()
