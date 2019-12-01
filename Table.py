from Attribute import *

class Table:

    def __init__(self, name: str, attrs=None):
        '''
        attrs: dict {attrname: attr}
        '''
        self.name = name
        self.attributes = {}
        self.rowsize = 0
        if attrs!=None:
            for attrname in attrs:
                self.addAttribute(attrname, attrs[attrname])
                



    def getAttribute(self, attrname: str):
        assert attrname in self.attributes.keys, "Wrong attribute name"
        return self.attributes[attrname]

    def getRowSize(self):
        return self.rowsize

    # 添加新的attribute
    def addAttribute(self, attrname, attr: Attribute):
        '''
        attrname: string
        attr: Attribute
        '''
        # 判断要添加的attribute是否已经存在
        assert attrname not in self.attributes.keys, "Attribute already exists"
        
        # 如果attr已经有value
        if attr.getSize()>0:
            # 如果有其它attr
            if len(self.attributes.keys)>1:
                if attr.getSize() != self.rowsize:
                    raise Exception("Attribute size does not match existed attributes")
            # 如果没有其它attr
            else:
                self.attributes[attrname] = attr
                self.rowsize = attr.getSize()
                return
        # 如果attr不包含value
        else:
            # 如果有其它attr并且其它attr带有value
            if len(self.attributes.keys)>1 and self.rowsize>0:
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




    def addTuple(self, row):
        '''
        row: dict {attrname: value}
        '''
        for attrname in row:
            assert attrname in self.attributes.keys, "Incompatible tuple"
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
            assert attrname in self.attributes.keys, "Incompatible tuple"
        for attrname in row:
            self.attributes[attrname].updateValue(index, row[attrname])




    # 暂不实现
    def project(self, attributes: list, table: Table):
        pass

    def select(self, attributes: list, conditions: list, reverse = False):
        '''
        attributes: * or list of attributes
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
                res.append[i]

        if reverse:
            res = res[::-1]

        table = Table('temp')
        if attributes == '*':
            attributes = self.attributes
        for attribute in attributes:
            table.addAttribute(self.attributes[attribute].getAttributeByIndex(res))

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
                res.append[i]

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
                res.append[i]
        
        for i in res:
            self.updateTuple(i, row)


if __name__ == "__main__":
