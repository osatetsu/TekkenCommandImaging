#! python

def move_symbol(symbol, x):
    '''
    '''
    result = []
    is_x = True
    for p in symbol:
        if is_x:
            result.append(p + x)
        else:
            result.append(p)
        is_x = not is_x

    return tuple(result)
