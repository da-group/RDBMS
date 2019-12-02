from Attribute import *

class Table:

    def __init__(self, name: str, attrs=None):
        '''
        attrs: list of attributes, primary attribute must be the first one in the list
        '''
        self.name = name
        self.attributes = {}
        self.rowsize = 0
        if attrs!=None:
            for attr in attrs:
                self.addAttribute(attr)
                
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
        assert attrname in self.attributes.keys, "Wrong attribute name"
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




    # 暂不实现
    def project(self, attributes: list, table):
        pass

    def select(self, attrnames: list, conditions: list, reverse = False):
        '''
        attrnames: * or list of attrnames
        return a table containing satisfied rows and their attributes
        '''
        res = []

        for i in range(self.rowsize):
            orFlag = False

            for orConds in conditions:
                andFlag = True

                for andconds in orConds:
                    key, func = andconds
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

        if reverse:
            res = res[::-1]

        table = Table('temp')
        if attrnames == '*':
            attrnames = self.attributes.keys()
        for attrname in attrnames:
            table.addAttribute(self.attributes[attrname].getAttributeByIndex(res))

        return table


    def delete(self, conditions):
        res = []

        for i in range(self.rowsize):
            orFlag = False

            for orConds in conditions:
                andFlag = True

                for andconds in orConds:
                    key, func = andconds
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
        res = []

        for i in range(self.rowsize):
            orFlag = False

            for orConds in conditions:
                andFlag = True

                for andconds in orConds:
                    key, func = andconds
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

    # TODO
    def groupBy(self, attributes):
        pass


if __name__ == "__main__":
    a1 = Attribute(name="a1", type=AttrTypes.INT, key=[AttrKeys.PRIMARY])
    a1.addValue(1)
    a2 = Attribute(name="a2", type=AttrTypes.VARCHAR, key=[AttrKeys.NOT_NULL])
    a2.addValue('hello')
    a3 = Attribute(name="a3", type=AttrTypes.FLOAT, key=[AttrKeys.NULL])

    t1 = Table('t1', [a1, a2, a3])
    print(t1)
    t1.addTuple({'a1':2,'a2':'world', 'a3':0.5})
    print(t1)
    t1.updateTuple(1,{'a1':5,'a2':'foooo', 'a3':2.5})
    print(t1)
    # t1.deleteTuple(0)
    # print(t1)
    # t2 = t1.select(["a1"], [[['a1',condition('inside', (1, 2), True)]]])
    t2 = t1.select("*", [[['a1',condition('inside', (1, 2))]]])
    print(t2)
    # t1.delete([[['a1',condition('inside', (1, 2))]]])
    # print(t1)
    t1.update([[['a1',condition('inside', (1, 2))]]], {'a1':100,'a2':'hhhhh', 'a3':3.14})
    print(t1)
