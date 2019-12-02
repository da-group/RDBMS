from Table import *
from Attribute import *
from Condition import *
from Parser import *

class Database():
    def __init__(self, name):
        self.name = name
        self.tables = {}    # {tablename: table}

    def __str__(self):
        res = "DatabaseName: "+self.name+"\n\n"
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
        self.tables[table.name] = table


    def dropTable(self, tableName):
        assert tableName in self.tables.keys(), 'Drop error: The table does not exists in the dataset'
        self.tables.pop(tableName)

    def join(self, joinParams):
        '''
        joinParams: 2 layer list [[table1_name, function_name, table2_name]]
        return table
        '''
        functions = {'greater': greaterOp,
                'smaller':smallerOp,
                'equal':equalOp,
                'not_equal':not_equalOp,
                'greater_equal':greater_equalOp,
                'smaller_equal':smaller_equalOp,
                }
        for joinParam in joinParams:
            # 解析joinCondition
            s1 = joinParam[0].split('.')
            table1 = self.getTableByName(s1[0])
            attrName1 = s1[1]
            s2 = joinParam[2].split('.')
            table2 = self.getTableByName(s2[0])
            attrName2 = s2[1]
            assert table1.name in self.tables.keys() and table2.name in self.tables.keys(), "Wrong join tables"
            assert attrName1 in table1.attributes.keys() and attrName2 in table2.attributes.keys(), "Wrong join attributes"
            funcName = joinParam[1]
            assert funcName in functions, "Wrong join function"

            # Nested join操作
            # for each tuple tr in r do begin 
            #   for each tuple ts in s do begin 
            #       test pair (tr,ts) tosee if they satisfy the join condition
            #       if they do, add tr^ts to the result. 
            #   end 
            # end

            res = [] # list of rows, rows: {attrname: value}
            for i in range(t1.rowsize):
                # 获取第一张表的tuple
                _a1, _t1, tuple1 = t1.getTuple(i)
                for j in range(t2.rowsize):
                    # 获取第二张表的tuple
                    _a2, _t2, tuple2 = t2.getTuple(j)
                    # 判断是否满足条件
                    b = functions[funcName](tuple1[attrName1], tuple2[attrName2], False)
                    if not b:
                        continue
                    # 如果满足条件
                    else:
                        tuple2.pop(attrName2)
                        row = {}
                        row.update(tuple1)
                        row.update(tuple2)
                        res.append(row)

            attrsAfterJoin = []
            for attrname in table1.attributes:
                attrsAfterJoin.append(table1.attributes[attrname].copyEmptyAttr())
            for attrname in table2.attributes:
                if attrname != attrName2:
                    attrsAfterJoin.append(table2.attributes[attrname].copyEmptyAttr())

            table = Table('join_result', attrsAfterJoin)
            for r in res:
                table.addTuple(r)
            return table





if __name__ == "__main__":
    d1 = Database('d1')
    # d1.createTable('t1')
    # d1.createTable('t2')
    # d1.dropTable('t1')
    # print(d1)

    a1 = Attribute(name="a1", type=AttrTypes.INT, key=[AttrKeys.PRIMARY])
    a1.addValue(1)
    a1.addValue(2)
    a1.addValue(4)
    a2 = Attribute(name="a2", type=AttrTypes.VARCHAR, key=[AttrKeys.NOT_NULL])
    a2.addValue("h")
    a2.addValue("e")
    a2.addValue("l")
    a3 = Attribute(name="a3", type=AttrTypes.INT, key=[AttrKeys.PRIMARY])
    a3.addValue(1)
    a3.addValue(2)
    a3.addValue(9)
    a4 = Attribute(name="a4", type=AttrTypes.VARCHAR, key=[AttrKeys.NOT_NULL])
    a4.addValue("w")
    a4.addValue("o")
    a4.addValue("r")
    a5 = Attribute(name="a5", type=AttrTypes.INT, key=[AttrKeys.NOT_NULL])
    a5.addValue(2)
    a5.addValue(2)
    a5.addValue(2)

    t1 = Table('t1', [a1, a2])
    t2 = Table('t2', [a3, a4, a5])

    d1.addTable(t1)
    d1.addTable(t2)

    statement = "t1, t2 on t1.a1 = t2.a5"
    p = parseJoins([statement])
    print(d1)
    print(d1.join(p))