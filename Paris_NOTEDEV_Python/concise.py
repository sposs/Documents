def func(a, b):
    return a+b

class MyClass(object):
    def __init__(self):
        self.attribute = None

    def class_meth(self, a):
        self.attribute = a


a = MyClass().class_meth(32)
