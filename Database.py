from Table import *
from Attribute import *
from Condition import *
from Parser import *
import pickle
import time
import math
import copy

class Database():
    def __init__(self, name):
        self.name = name
        self.tables = {}    # {tablename: table}
        self.foreignKeys = {}   # { t1: [{a1:(t2,a2,"cascade")}] }
        self.filePath = "./data/"+name+".db"

    def __str__(self):
        res = "DatabaseName: "+self.name+"\n\n"
        for tableName in self.tables:
            res += "TableName: "+tableName+"\n"
            res += "TableAttributes: "+ str(self.tables[tableName].attributes.keys())+"\n"
            res += "\n"
        return res

    def saveToFile(self, path = None):
        if path is None:
            path = self.filePath
        f = open(path, "wb")
        pickle.dump(self, f)

    # 查看数据库内table名称
    def getTableNames(self):
        return self.tables.keys()

    # 指定表名, 获取表对象
    def getTableByName(self, tableName: str):
        # print(self.tables.keys())
        assert tableName in self.tables.keys(), "The table does not exist "+tableName
        return self.tables[tableName]


    def createTable(self, tableName: str, attrs=None):
        '''
        attrs: list of attributes, primary attribute must be the first one in the list
        '''
        assert tableName not in self.tables.keys(), 'Create error: The table already exists in the dataset'
        self.tables[tableName] = Table(tableName, attrs)


    def addTable(self, table):
        assert table.name not in self.tables.keys(), 'Add error: The table already exists in the dataset '+table.name
        self.tables[table.name] = table


    def dropTable(self, tableName):
        assert tableName in self.tables.keys(), 'Drop error: The table does not exists in the dataset'
        self.tables.pop(tableName)


    def join(self, joinParams, name = None):
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
            funcName = joinParam[1]
            s2 = joinParam[2].split('.')
            t1 = self.getTableByName(s1[0])
            t2 = self.getTableByName(s2[0])
            attrName1 = s1[1]
            attrName2 = s2[1]
            assert t1.name in self.tables.keys() and t2.name in self.tables.keys(), "Wrong join tables"
            assert attrName1 in t1.attributes.keys() and attrName2 in t2.attributes.keys(), "Wrong join attributes"
            assert funcName in functions, "Wrong join function"
            
            res = [] # list of rows, rows: {attrname: value}
            # 如果两个表tuple数量差距十分大e.g |a1|<lg(|a2|) 用nested-loop
            size1 = t1.attributes[attrName1].getSize()
            size2 = t2.attributes[attrName2].getSize()


            attrsAfterJoin = []
            for attrname in t1.attributes:
                attrsAfterJoin.append(t1.attributes[attrname].copyEmptyAttr())
            for attrname in t2.attributes:
                if attrname != attrName2:
                    attrsAfterJoin.append(t2.attributes[attrname].copyEmptyAttr())

            table = None
            if name is not None:
                table = Table(name, attrsAfterJoin)
            else:
                table = Table('join_result', attrsAfterJoin)

            time1 = time.time()
            if size1 < math.log2(size2) or size2 < math.log2(size1) or funcName != "equal":
            # if True:
                # join using nested-loop
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
                            # res.append(row)
                            table.addTuple(row)
            else:
                '''
                join using merge-scan:
                http://www.dcs.ed.ac.uk/home/tz/phd/thesis/node20.htm
                '''
                sortedIndices1 = t1.attributes[attrName1].getSortedIndexList()
                sortedIndices2 = t2.attributes[attrName2].getSortedIndexList()

                i = j = 0
                while i<len(sortedIndices1) and j<len(sortedIndices2):
                    _a1, _t1, tuple1 = t1.getTuple(sortedIndices1[i])
                    _a2, _t2, tuple2 = t2.getTuple(sortedIndices2[j])
                    if tuple1[attrName1] > tuple2[attrName2]:
                        j += 1
                    elif tuple1[attrName1] < tuple2[attrName2]:
                        i += 1
                    else:
                        copy_tuple2 = copy.deepcopy(tuple2)
                        copy_tuple2.pop(attrName2)
                        row = {}
                        row.update(tuple1)
                        row.update(copy_tuple2)
                        # res.append(row)
                        table.addTuple(row)

                        jj = j+1
                        while jj<len(sortedIndices2):
                            _a2, _t2, tuple2_temp = t2.getTuple(sortedIndices2[jj])
                            if tuple1[attrName1] == tuple2_temp[attrName2]:
                                copy_tuple2_temp = copy.deepcopy(tuple2_temp)
                                copy_tuple2_temp.pop(attrName2)
                                row = {}
                                row.update(tuple1)
                                row.update(copy_tuple2_temp)
                                # res.append(row)
                                table.addTuple(row)
                                jj += 1
                            else: break
                        
                        ii = i+1
                        while ii<len(sortedIndices1):
                            _a1, _t1, tuple1_temp = t1.getTuple(sortedIndices1[ii])
                            if tuple1_temp[attrName1] == tuple2[attrName2]:
                                copy_tuple2_temp = copy.deepcopy(tuple2_temp)
                                copy_tuple2_temp.pop(attrName2)
                                row = {}
                                row.update(tuple1_temp)
                                row.update(copy_tuple2_temp)
                                # res.append(row)
                                table.addTuple(row)

                                ii += 1
                            else: break
                            
                        i += 1
                        j += 1

            time2 = time.time()
            print("join time on "+t1.name+" "+t2.name+" "+str(time2-time1))

            return table


    def addForeignKey(self, t1, a1, t2, a2, onDelete = "set null"):
        '''
        t1,a1,t2,a2, ondelete: str, table1_name, attribute1_name, table2_name, attribute2_name, on delete operation
        '''
        assert t1 in self.tables and t2 in self.tables, "Wrong tables"
        assert a1 in self.tables[t1].attributes and a2 in self.tables[t2].attributes, "attribute doesn't match table"

        if t1 not in self.foreignKeys:
            self.foreignKeys[t1] = [{a1:(t2,a2,onDelete)}]
        else:
            self.foreignKeys[t1].append({a1:(t2,a2,onDelete)})


    def delForeignKey(self, t1, a1):
        assert t1 in self.foreignKeys, "Wrong table"
        for i, dic in enumerate(self.foreignKeys[t1]):
            if a1 in dic: 
                self.foreignKeys[t1].pop(i)
                break
        else:
            raise Exception("Wrong attributes")


    def showForeignKeys(self):
        return str(self.foreignKeys)
        



if __name__ == "__main__":
    d1 = Database('d1')
    # d1.createTable('t1')
    # d1.createTable('t2')
    # d1.dropTable('t1')
    # print(d1)

    #====================================test1=========================================
    # a1 = Attribute(name="a1", type=AttrTypes.INT, key=[AttrKeys.PRIMARY])
    # a1.addValue(1)
    # a1.addValue(2)
    # a1.addValue(4)
    # a2 = Attribute(name="a2", type=AttrTypes.VARCHAR, key=[AttrKeys.NOT_NULL])
    # a2.addValue("h")
    # a2.addValue("e")
    # a2.addValue("l")
    # a3 = Attribute(name="a3", type=AttrTypes.INT, key=[AttrKeys.PRIMARY])
    # a3.addValue(1)
    # a3.addValue(2)
    # a3.addValue(9)
    # a4 = Attribute(name="a4", type=AttrTypes.VARCHAR, key=[AttrKeys.NOT_NULL])
    # a4.addValue("w")
    # a4.addValue("o")
    # a4.addValue("r")
    # a5 = Attribute(name="a5", type=AttrTypes.INT, key=[AttrKeys.NOT_NULL])
    # a5.addValue(3)
    # a5.addValue(2)
    # a5.addValue(2)

    # t1 = Table('t1', [a1, a2])
    # t2 = Table('t2', [a3, a4, a5])

    # f1 = open("./data/t1.tb", "wb")
    # pickle.dump(t1, f1)
    # f1 = open("./data/t1.tb", "rb")
    # t1 = pickle.load(f1)
    # print(t1)

    # d1.addTable(t1)
    # d1.addTable(t2)

    # statement = "t1, t2 on t1.a1 = t2.a3"
    # p = parseJoins([statement])
    # print(d1)
    # print(d1.join(p))
    # join_table = d1.join(p)
    # select_table = join_table.select("*", [[['a1',condition('inside', (1, 2))]]])
    # print(select_table)

    # d1.addForeignKey("t1", "a1", "t2", "a3")
    # d1.addForeignKey("t2", "a3", "t1", "a2")
    # print(d1.showForeignKeys())


    # ===============================test join time===================================
    a1 = Attribute(name="a1", type=AttrTypes.INT, key=[AttrKeys.NOT_NULL])
    for i in range(1,1001):
        a1.addValue(i)
    a2 = Attribute(name="a2", type=AttrTypes.INT, key=[AttrKeys.NOT_NULL])
    for i in range(1,1001):
        a2.addValue(1)
    a3 = Attribute(name="a3", type=AttrTypes.INT, key=[AttrKeys.PRIMARY])
    for i in range(1,10001):
        a3.addValue(i)
    a4 = Attribute(name="a4", type=AttrTypes.INT, key=[AttrKeys.NOT_NULL])
    for i in range(1,10001):
        a4.addValue(1)

    t1 = Table('t1', [a1, a2])
    t2 = Table('t2', [a3, a4])

    d1.addTable(t1)
    d1.addTable(t2)

    statement = "t1, t2 on t1.a1 = t2.a3"
    p = parseJoins([statement])

    time1 = time.time()
    join_table = d1.join(p)
    print(join_table.rowsize)
    time2 = time.time()
    print(time2-time1)
