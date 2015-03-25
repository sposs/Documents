x, y = symbols("x y", positive=True, real=True)
def g(x, ac, bc, cabc):
    return  (1-x)*ac + x * bc - x*(1-x)*cabc
cgainp = 0.65
cgainas =  0.477
cinasp = 0.1
cgaasp = 0.19
gaas = 1.423
inas = 0.356
inp = 1.353
gap = 2.777
fgainasp=x*(1-x)*((1-y)*g(x,gap,inp,cgainp)\
           + y*g(x, gaas, inas, cgainas))\
           + y*(1-y)*(x*g(y, 2.88, 1.42, cgaasp)\
           + (1-x)*g(y, 1.4236, 0.417, cinasp))
fgainasp /= (x*(1-x) + y*(1-y))


