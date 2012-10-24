#import statements not added
ga = GenericApplication()
ga.setScript("myscript.py")
ga.setArguments("some args")

root = RootScript({"Script":"/path/to/script.exe",
                   "Arguments":"1,2,3"})
root.getInputFromApp(ga)

d = DiracILC()
j = UserJob()
res =j.append(ga)
if not res['OK']:
  print res['Message']
  exit(1)
res =j.append(root)
if not res['OK']:
  print res['Message']
  exit(1)
print j.submit(d)
