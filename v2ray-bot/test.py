def a():
    try:
        u = 5 / 0
        return 'a'
    except Exception as e:
        raise e

def b():
    c = a()
    print('ok')

b()