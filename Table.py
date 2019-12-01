
class Table:

    def __init__(self, ** args):
        self.attributes = {}
        self.rowsize = 0

    
    def add_attribute(self, attrname, attr):
        '''
        attrname: string
        attr: Attribute
        '''
        assert attrname not in self.attributes.keys, "Attribute already exists"
        self.attributes[attrname] = attr
        
        
    def get_attribute(self, attrname):
        assert attrname in self.attributes.keys, "Wrong attribute name"
        return self.attributes[attrname]

    def insert(self, tuple):
        '''
        tuple: dict {attrname: value}
        '''
        

    def delete(self, conditions):
        pass

    def select(self, attributes: list, conditions: dict):
        '''
        return new table containing satisfied rows and their attributes
        '''
        

if __name__ == "__main__":