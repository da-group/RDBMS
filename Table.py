from Attribute import *
from Parser import *
from Parser import parseConditionTuple
from Type import *
import copy
import time

class Table:

    def __init__(self, name: str, attrs=None):
        '''
        attrs: list of attributes, primary attribute must be the first one in the list
        '''
        self.name = name
        self.attributes = {}
        self.rowsize = 0
        self.pk = []
        if attrs!=None:
            for attr in attrs:
                self.addAttribute(attr)
                # 如果是主键的话记录下来
                if AttrKeys.PRIMARY in attr.key:
                    self.pk.append(attr.name)
                
    def __str__(self):
        res = "TableName: "+self.name+"\n"
        for attrname in self.attributes:
            res += attrname+"    "
        res += "\n"
        for i in range(self.rowsize):
            _a, tupleValues, _av = self.getTuple(i)
            for v in tupleValues:
                res += str(v)+"    "
            res +='\n'
        return res


    def getAttribute(self, attrname: str):
        assert attrname in self.attributes.keys(), "Wrong attribute name"
        return self.attributes[attrname]

    def getRowSize(self):
        return self.rowsize

    # 添加新的attribute
    def addAttribute(self, attr: Attribute):
        '''
        attr: Attribute
        '''
        # 判断要添加的attribute是否已经存在
        attrname = attr.name
        assert attrname not in self.attributes.keys(), "Attribute already exists"
        
        # 如果attr已经有value
        if attr.getSize()>0:
            # 如果有其它attr
            if len(self.attributes.keys())>0:
                if attr.getSize() != self.rowsize:
                    raise Exception("Attribute size does not match existed attributes")
                else:
                    self.attributes[attrname] = attr
            # 如果没有其它attr
            else:
                self.attributes[attrname] = attr
                self.rowsize = attr.getSize()
                return
        # 如果attr不包含value
        else:
            # 如果有其它attr并且其它attr带有value
            if len(self.attributes.keys())>0 and self.rowsize>0:
                #用None来填充
                for i in range(self.rowsize):
                    attr.addValue(None)
                self.attributes[attrname] = attr
                return 
            # 如果没有其它attr
            else:
                self.attributes[attrname] = attr
        
    # 暂不实现    
    def deleteAttribute(self, attrname):
        pass

    # 暂不实现
    def updateAttribute(self, attrname, attr):
        pass



    def getTuple(self, index: int):
        attrnames = []
        values = []
        attrnamesAndValues = {}
        for attrname in self.attributes:
            attrnames.append(attrname)
            value = self.attributes[attrname][index]
            values.append(value)
            attrnamesAndValues[attrname] = value
        return attrnames, values, attrnamesAndValues

    def addTuple(self, row):
        '''
        row: dict {attrname: value}
        '''
        for attrname in row:
            assert attrname in self.attributes.keys(), "Incompatible tuple"
        for attrname in self.attributes:
            if attrname in row:
                self.attributes[attrname].addValue(row[attrname])
            else:
                self.attributes[attrname].addValue(None)
        self.rowsize += 1

    def insertTuple(self, row):
        '''
        在addTuple的基础上判断是否有primary key重复的问题
        '''
        for pk_name in self.pk:
            assert pk_name in row.keys(), "The tuple must contain primary key"
        
        l = None
        for j, pk_name in enumerate(self.pk):
            if j == 0:
                l = [i for i,v in enumerate(self.attributes[pk_name].getValues()) if v == row[pk_name]]
            else:
                l2 = [i for i,v in enumerate(self.attributes[pk_name].getValues()) if v == row[pk_name]]
                l = list(set(l).intersection(set(l2)))
        if l != []:
            raise Exception("Duplicate primary key value error")

        self.addTuple(row)
        

    def deleteTuple(self, index):
        '''
        index: integer or list
        '''
        if isinstance(index, int): index = [index]
        for attrname in self.attributes:
            self.attributes[attrname].deleteValue(index)
        self.rowsize -= len(index)

    def updateTuple(self, index, row):
        '''
        index: integer
        row: dict {attrname: value}
        '''
        for attrname in row:
            assert attrname in self.attributes.keys(), "Incompatible tuple"
        for attrname in row:
            self.attributes[attrname].updateValue(index, row[attrname])


    # 可能有重复行
    def project(self, attrnames: list, name = None):
        table = None
        if name is not None:
            table = Table(name)
        else:
            table = Table('project_result')
        if attrnames == '*':
            attrnames = self.attributes.keys()
        for attrname in attrnames:
            table.addAttribute(self.attributes[attrname])
        return table

    def select(self, attrnames: list, conditions=None, name=None, reverse = False):
        '''
        attrnames: * or list of attrnames
        return a table containing satisfied rows and their attributes
        '''
        #判断attrnames是不是都在该表内
        if isinstance(attrnames, list):
            for attrname in attrnames:
                assert attrname in self.attributes.keys(), "Select non-existent attribute"

        res = []

        if conditions is None:
            res = range(self.rowsize)
        else:
            time1 = time.time()
            # 如果有index用index
            print(attrnames)
            print(len(attrnames))
            print(conditions)
            if isinstance(attrnames, list) and len(attrnames) == 1 \
                    and self.attributes[attrnames[0]].btree is not None \
                    and len(conditions) == 1 and len(conditions[0]) == 1 \
                    and conditions[0][0][0] == attrnames[0] \
                    and conditions[0][0][1][0] in ["=","inside",">","<",">=","<="]:
                
                print("using index")
                
                c = conditions[0][0][1]
                if c[0] == "=":
                    target = int(c[1][0])
                elif c[0] == ">":
                    target = (int(c[1][0])+1, float("inf"))
                elif c[0] == "<":
                    target = (float("-inf"), int(c[1][0])-1)
                elif c[0] == ">=":
                    target = (int(c[1][0]), float("inf"))
                elif c[0] == "<=":
                    target = (float("-inf"), int(c[1][0]))
                elif c[0] == "inside":
                    l = c[1]
                    l[0] = int(c[1][0])
                    l[1] = int(c[1][1])
                    target = tuple(l)
                    
                res = self.attributes[attrnames[0]].getIndexWithBPlusTree(target)

            else: # 没有index
                for i in range(self.rowsize):
                    orFlag = False
                    for orConds in conditions:
                        andFlag = True
                        for andconds in orConds:
                            key, func = andconds
                            a, b, c = func
                            func = parseConditionTuple(a, b, c)
                            s = key.split(".")
                            if len(s) == 1:
                                attrname = s[0]
                            elif len(s) == 2:
                                tablename = s[0]
                                if tablename != self.name:
                                    continue
                                attrname = s[1]
                            else:
                                raise Exception("Wrong conditions")
                            
                            b = func(self.attributes[attrname][i])
                            if not b:
                                andFlag = False
                                break
                        if andFlag:
                            orFlag = True
                            break
                    if orFlag:
                        res.append(i)
            time2 = time.time()
            print(self.name+" select time: "+str(time2-time1))

        if reverse:
            res = res[::-1]

        table = None
        if name is not None:
            table = Table(name)
        else:
            table = Table('select_result')
        if attrnames == '*':
            attrnames = self.attributes.keys()
        for attrname in attrnames:
            table.addAttribute(self.attributes[attrname].getAttributeByIndex(res))

        return table


    def delete(self, conditions=None):
        if conditions is None:
            self.deleteTuple(range(self.rowsize))
            return
                
        res = []

        for i in range(self.rowsize):
            orFlag = False
            for orConds in conditions:
                andFlag = True
                for andconds in orConds:
                    key, func = andconds
                    func = parseConditionTuple(*func)
                    s = key.split(".")
                    if len(s) == 1:
                        attrname = s[0]
                    elif len(s) == 2:
                        tablename = s[0]
                        if tablename != self.name:
                            continue
                        attrname = s[1]
                    else:
                        raise Exception("Wrong conditions")
                    
                    b = func(self.attributes[attrname][i])
                    if not b:
                        andFlag = False
                        break
                if andFlag:
                    orFlag = True
                    break
            if orFlag:
                res.append(i)

        self.deleteTuple(res)
        

    def update(self, conditions, row):
        for attrname in row:
            assert attrname not in self.pk, "Can not modify primary key"

        res = []

        for i in range(self.rowsize):
            orFlag = False
            for orConds in conditions:
                andFlag = True
                for andconds in orConds:
                    key, func = andconds
                    func = parseConditionTuple(*func)
                    s = key.split(".")
                    if len(s) == 1:
                        attrname = s[0]
                    elif len(s) == 2:
                        tablename = s[0]
                        if tablename != self.name:
                            continue
                        attrname = s[1]
                    else:
                        raise Exception("Wrong conditions")
                    
                    b = func(self.attributes[attrname][i])
                    if not b:
                        andFlag = False
                        break
                if andFlag:
                    orFlag = True
                    break
            if orFlag:
                res.append(i)
        
        for i in res:
            self.updateTuple(i, row)


    def groupByHaving(self, attrnames, havingConditions = None):
        '''
        attrnames: list of attribute names []
        return list of tables
        # '''
        for attrname in attrnames:
            assert attrname in self.attributes.keys(), "Wrong attribute names"
        res = []
        res = self.groupByRecursion(attrnames, [self], 0)

        if havingConditions is None:
            return res
        else:
            # 根据having的condition来筛选返回的table
            new_res = []
            for table in res:
                orFlag = False
                for orConds in havingConditions:
                    andFlag = True
                    for andconds in orConds:
                        key, sfunc, cfunc = andconds

                        s = key.split(".")
                        if len(s) == 1:
                            attrname = s[0]
                        elif len(s) == 2:
                            tablename = s[0]
                            if tablename != self.name:
                                continue
                            attrname = s[1]
                        else:
                            raise Exception("Wrong conditions")
                        
                        aggregateResult = sfunc(table.attributes[attrname])
                        # cfunc = parseConditionTuple(*cfunc)

                        b = cfunc(aggregateResult)
                        if not b:
                            andFlag = False
                            break
                    if andFlag:
                        orFlag = True
                        break
                if orFlag:
                    new_res.append(table)
            return new_res


    def groupByRecursion(self, attrnames, tables, layer):
        '''
        attrnames: list of attribute names []
        tables: list of tables
        '''
        if not attrnames:
            return tables
        else:
            attrname = attrnames.pop(0)
            res = []
            for t in tables:
                res.extend(t.groupBySingleAttribute(attrname))
                res = self.groupByRecursion(copy.deepcopy(attrnames), res, layer+1)
            return res

    def groupBySingleAttribute(self, attrname):
        '''
        attrname: str
        return list of tables
        '''
        assert attrname in self.attributes.keys(), "Wrong attribute names"

        attrsForTable = []
        for a in self.attributes:
            attrsForTable.append(self.attributes[a].copyEmptyAttr())

        res = {}    # {value, table}
        for i in range(self.rowsize):
            emptyAttrs = copy.deepcopy(attrsForTable)
            _a, _t, tup = self.getTuple(i)
            # 如果遇到新的value, 创建一个新表
            if tup[attrname] not in res.keys():
                table = Table("temp",emptyAttrs)
                table.addTuple(tup)
                res[tup[attrname]] = table
            # 如果value已经存在，则直接加入相对应的表
            else:
                table = res[tup[attrname]]
                table.addTuple(tup)
        return [ v for v in res.values() ]









if __name__ == "__main__":

    #===============================test1===========================================
    # a1 = Attribute(name="a1", type=AttrTypes.INT, key=[AttrKeys.PRIMARY])
    # a1.addValue(1)
    # a2 = Attribute(name="a2", type=AttrTypes.VARCHAR, key=[AttrKeys.NOT_NULL])
    # a2.addValue('hello')
    # a3 = Attribute(name="a3", type=AttrTypes.FLOAT, key=[AttrKeys.NULL])

    # t1 = Table('t1', [a1, a2, a3])
    # print(t1)
    # t1.insertTuple({'a1':2,'a2':'world', 'a3':0.5})
    # t1.insertTuple({'a1':2,'a2':'world', 'a3':0.5})
    # print(t1)
    # t1.updateTuple(1,{'a1':5,'a2':'foooo', 'a3':2.5})
    # print(t1)
    # # t1.deleteTuple(0)
    # # print(t1)
    # # t2 = t1.select(["a1"], [[['a1',condition('inside', (1, 2), True)]]])
    # t2 = t1.select("*", [[['a1',('inside', (1, 2))]]])
    # print(t2)
    # # t1.delete([[['a1',condition('inside', (1, 2))]]])
    # # print(t1)
    # # t1.delete()
    # # print(t1)
    # t1.update([[['a1',condition('inside', (1, 2))]]], {'a2':'hhhhh', 'a3':3.14})
    # print(t1)


    #===============================test2=join======================================
    a1 = Attribute(name="a1", type=AttrTypes.INT, key=[AttrKeys.PRIMARY])
    a1.addValue(1)
    a1.addValue(1)
    a1.addValue(1)
    a1.addValue(1)
    a1.addValue(2)
    a1.addValue(2)
    a2 = Attribute(name="a2", type=AttrTypes.INT, key=[AttrKeys.NOT_NULL])
    a2.addValue(2)
    a2.addValue(2)
    a2.addValue(3)
    a2.addValue(3)
    a2.addValue(2)
    a2.addValue(2)
    a3 = Attribute(name="a3", type=AttrTypes.INT, key=[AttrKeys.NULL])
    a3.addValue(3)
    a3.addValue(9)
    a3.addValue(3)
    a3.addValue(9)
    a3.addValue(3)
    a3.addValue(9)
    t1 = Table('t1', [a1, a2, a3])
    statement = "a1,a3"
    ass = parseGroups(statement)
    havingState = "avg(t1.a1) > 1"
    ph = parseHaving(havingState)
    groupByResult = t1.groupByHaving(ass, ph)
    for t in groupByResult:
        print(t)
        

    #============================test time====================
    # a1 = Attribute(name="a1", type=AttrTypes.INT, key=[AttrKeys.NOT_NULL])
    # for i in range(12, 10000):
    #     for j in range(100):
    #         a1.addValue(i)
    # t1 = time.time()
    # a1.getIndexByCondition(condition('inside', (3, 10)))
    # t2 = time.time()
    # print(t2-t1)

    # a1 = Attribute(name="a1", type=AttrTypes.INT, key=[AttrKeys.NOT_NULL])
    # for i in range(1,1001):
    #     a1.addValue(i)
    # a2 = Attribute(name="a2", type=AttrTypes.INT, key=[AttrKeys.NOT_NULL])
    # for i in range(1,1001):
    #     a2.addValue(i)

    # a1.buildIndex(10)
    # t1 = Table('t1', [a1, a2])
    # res = t1.select(["a1"], [[['a1',('inside', ['2', '5'], False)]]])
    # print(res)

