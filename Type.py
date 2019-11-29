from enum import Enum
from datetime import date


TypeDict = {
    'int': int,
    'float': float,
    'varchar': str,
    'data': date,
    'INT': int,
    'FLOAT': float,
    'VARCHAR': str, 
    'DATE': date
}


class AttrTypes(Enum):
    INT = 'int'
    FLOAT = 'float'
    VARCHAR = 'varchar'
    DATE = 'date'


class AttrKeys(Enum):
    PRIMARY = 'PRIMARY KEY'
    INCREMENT = 'AUTO_INCREMENT'
    NOT_NULL = 'NOT NULL'
    NULL = 'NULL'



if __name__ == '__main__':
    t = AttrTypes.INT
    print(t)
    print(TypeDict[t.value])