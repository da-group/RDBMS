


def condition(func, target, ifNot=False):
    functions = {'greater': greaterOp,
                'in': inOp,
                'inside': insideOp}
    def wrapper(value):
        # nothing but find the function
        return functions[func](value, target, ifNot)
    return wrapper


def greaterOp(value, target, ifNot):
    if ifNot:
        return value<=target
    return value>target

def inOp(value, target, ifNot):
    if ifNot:
        return not value in target
    return value in target


def insideOp(value, target, ifNot):
    start, end = target
    if ifNot:
        return not (value>=start and value<=end)
    return value>=start and value<=end


if __name__ == '__main__':
    f = condition('inside', (1, 2), True)
    print(f(1.5))