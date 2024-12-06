from sympy import *

r, a_0, A = symbols('r, a_0, A')

eq1 = (A*r**3*exp(-r/(3*a_0)))**2

eq1_diff = eq1.diff(r)

eq2 = Eq(eq1_diff, 0)

soln = solve(eq2, r)

print(soln)
