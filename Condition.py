


def condition(func, target):
    functions = {'greater': greaterOp,
                'in': inOp}
    def wrapper(value):
        # nothing but find the function
        return functions[func](value, target)
    return wrapper


def greaterOp(value, target):
    return value>target

def inOp(value, target):
    return value in target


if __name__ == '__main__':
    f = condition('in', [1, 2])
    print(f(1.0))