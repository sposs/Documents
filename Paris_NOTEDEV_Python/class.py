from parent import Parent

class MyObject(Parent):
    def __init__(self, arg):
        super(MyObject, self).__init__(self, arg)

    def my_function(self, a):
        return a
    
    def my_other_func(self):
        pass
