>>> from sympy import *
>>> init_printing(use_unicode=False, wrap_line=False, no_global=True)
>>> x = Symbol('x')
>>> integrate(x**2 + x + 1, x)
 3    2
x    x
-- + -- + x
3    2 
>>> integrate(x/(x**2+2*x+1), x)
               1  
log(x + 1) + -----
             x + 1
>>> integrate(exp(-x**2)*erf(x), x)
  ____    2   
\/ pi *erf (x)
--------------
      4   
