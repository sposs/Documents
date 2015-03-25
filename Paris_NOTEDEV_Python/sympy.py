from sympy import symbols, simplify
from sympy import factor, cancel, powsimp
from sympy import limit
x, y, z = symbols("x y z", positive=True, 
                  real=True)
fabd=1.347+0.643*x+0.786*x*x 
fabc=0.36+0.505*x+0.555*x*x 
facd=1.347-1.083*y+0.091*y*y 
fbcd=2.74-1.473*y+0.146*y*y 
term1=x*(1.-x)* ( (1.-y)*fabd+y*fabc ) 
term2=y*(1.-y)*( (1.-x)*facd+x*fbcd ) 
term3=x*(1.-x)+y*(1.-y) 
res_cl = (term1+term2)/term3
print res_cl.subs(x, 0.250).subs(y, 0.543)

