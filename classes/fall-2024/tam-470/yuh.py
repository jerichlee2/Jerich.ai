from sympy import *

lmbda1, lmbda2, c, k = symbols('lmbda1, lmbda2, c, k')

eq1 = Eq(lmbda1, (-c+sqrt(c**2-4*k))/2)
eq2 = Eq(lmbda2, (-c-sqrt(c**2-4*k))/2)
eq3 = Eq(lmbda1, -2+.5*I)
eq4 = Eq(lmbda2, -2-.5*I)

soln = solve((eq1,eq2,eq3), c, k)
print(soln)
