

def a():
    return {'a': 2}


def b():
    s = {'kos': 2}
    s.update(a())
    return s


print(b())
