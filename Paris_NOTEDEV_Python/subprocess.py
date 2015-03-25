import subprocess as sp
res = sp.check_output(["/usr/bin/ls", "-l"])
print res
