a = {"abc": 23, "something": "else", 
     345: "toto"}
a["test"] = MyObject()
print a.keys()
# returns ['abc', 'something', 345, 'test']
print a.values()
# returns [23, "else", "toto", <__main__.MyObject instance at 0x7faf209e5368>]
print "abc" in a
# returns True

