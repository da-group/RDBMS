
import re

def condition(func, target,ifNot=False):
    functions = {'greater': greaterOp,
                 'smaller':smallerOp,
                 'equal':equalOp,
                 'not_equal':not_equalOp,
                 'greater_equal':greater_equalOp,
                 'smaller_equal':smaller_equalOp,
                 'in': inOp,
                 'inside':insideOp,
                 'like':likeOp}
    def wrapper(value):
        # nothing but find the function
        return functions[func](value, target)
    return wrapper


def greaterOp(value, target,ifNot):
    if ifNot:
        return value <= target
    return value>target


def smallerOp(value,target,ifNot):
    if ifNot:
        return value >= target
    return value<target

def equalOp(value,target,ifNot):
    if ifNot:
        return value != target
    return value == target

def not_equalOp(value,target,ifNot):
    if ifNot:
        return value == target
    return value != target

def greater_equalOp(value,target,ifNot):
    if ifNot:
        return value < target
    return value >= target

def smaller_equalOp(value,target,ifNot):
    if ifNot:
        return value > target
    return value <= target

def inOp(value, target,ifNot):
    if ifNot:
        return value not in target
    return value in target

def insideOp(value, target, ifNot):
    start, end = target
    if ifNot:
        return not (value>=start and value<=end)
    return value>=start and value<=end

def likeOp(value,target,ifNot):   
    target = target.split("%")
    
    for i in range(0,len(target)):
        temp = list(target[i])
        repeat = 0
        for j in range(0,len(temp)):
            if temp[j] == "_":
                repeat+= 1
                if j == len(temp)-1 or (j < len(temp)-1 and temp[j+1] != "_" ):
                    temp[j] = ".{"+str(repeat)+"}"
                    repeat = 0
        t = ''.join(temp)
        target[i] = t.replace("_",'')
    
    target = '.*'.join(target)
    
    regex = re.compile(r''+target+'')
    if(re.fullmatch(regex,value)):
          if ifNot: return False
          return True
    if ifNot: return True
    return False
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    

if __name__ == '__main__':
    f = condition('in', [1, 2])
    print(f(1.0))