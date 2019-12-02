from Table import *

class Database():
    def __init__(self, name):
        self.name = name
        self.tables = {}    # {tablename: table}

    def __str__(self):
        res = "DatebaseName: "+self.name+"\n\n"
        for tableName in self.tables:
            res += "TableName: "+tableName+"\n"
            res += "TableAttributes: "+ str(self.tables[tableName].attributes.keys())+"\n"
            res += "\n"
        return res

    # 查看数据库内table名称
    def getTableNames(self):
        return self.tables.keys()

    # 指定表名, 获取表对象
    def getTableByName(self, tableName: str):
        assert tableName in self.tables.keys(), "The table does not exist"
        return self.tables[tableName]


    def createTable(self, tableName: str, attrs=None):
        '''
        attrs: list of attributes, primary attribute must be the first one in the list
        '''
        assert tableName not in self.tables.keys(), 'Create error: The table already exists in the dataset'
        self.tables[tableName] = Table(tableName, attrs)


    def addTable(self, table):
        assert table.name not in self.tables.keys(), 'Add error: The table already exists in the dataset'
        self.tables[tableName] = table


    def dropTable(self, tableName):
        assert tableName in self.tables.keys(), 'Drop error: The table does not exists in the dataset'
        self.tables.pop(tableName)

if __name__ == "__main__":
    d1 = Database('d1')
    d1.createTable('t1')
    d1.createTable('t2')
    d1.dropTable('t1')
    print(d1)

