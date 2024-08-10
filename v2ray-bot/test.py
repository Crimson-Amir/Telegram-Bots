class A:
    b = 0
    def __init__(self):
        self.c = 1

    def run_it(self):
        print(self.b)



d = A()
d.run_it()
b = A()
b.b = 2
d.run_it()