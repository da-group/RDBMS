from enum import Enum
from datetime import datetime


TypeDict = {
    'int': int,
    'float': float,
    'varchar': str,
    'date': datetime,
    'INT': int,
    'FLOAT': float,
    'VARCHAR': str, 
    'DATE': datetime
}


class AttrTypes(Enum):
    INT = 'int'
    FLOAT = 'float'
    VARCHAR = 'varchar'
    DATE = 'date'


class AttrKeys(Enum):
    PRIMARY = 'PRIMARY KEY'
    NOT_NULL = 'NOT NULL'
    NULL = 'NULL'



if __name__ == '__main__':
    t = AttrTypes.INT
    print(t)
    print(TypeDict[t.value])