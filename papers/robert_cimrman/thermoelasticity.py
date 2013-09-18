import numpy as np

from sfepy.fem import (Mesh, Domain, Field,
                       FieldVariable,
                       Material, Integral,
                       Equation, Equations,
                       ProblemDefinition)
from sfepy.terms import Term
from sfepy.fem.conditions import Conditions, EssentialBC
from sfepy.solvers.ls import ScipyDirect
from sfepy.solvers.nls import Newton
from sfepy.postprocess import Viewer

mesh = Mesh.from_file('meshes/2d/square_tri2.mesh')
domain = Domain('domain', mesh)

omega = domain.create_region('Omega', 'all')
left = domain.create_region('Left',
                            'vertices in x < -0.999',
                            'facet')
right = domain.create_region('Right',
                             'vertices in x > 0.999',
                             'facet')
bottom = domain.create_region('Bottom',
                              'vertices in y < -0.999',
                              'facet')
top = domain.create_region('Top',
                           'vertices in y > 0.999',
                           'facet')

domain.save_regions_as_groups('regions.vtk')

field_t = Field.from_args('temperature', np.float64,
                          'scalar', omega, 2)
t = FieldVariable('t', 'unknown', field_t, 1)
s = FieldVariable('s', 'test', field_t, 1,
                  primary_var_name='t')

integral = Integral('i', order=2)

term = Term.new('dw_laplace(s, t)', integral, omega,
                s=s, t=t)
eq = Equation('temperature', term)
eqs = Equations([eq])

t_left = EssentialBC('t_left',
                     left, {'t.0' : 10.0})
t_right = EssentialBC('t_right',
                      right, {'t.0' : 30.0})

ls = ScipyDirect({})
nls = Newton({}, lin_solver=ls)

pb = ProblemDefinition('temperature', equations=eqs,
                       nls=nls, ls=ls)
pb.time_update(ebcs=Conditions([t_left, t_right]))

temperature = pb.solve()
out = temperature.create_output_dict()

field_u = Field.from_args('displacement', np.float64,
                          'vector', omega, 1)
u = FieldVariable('u', 'unknown', field_u, mesh.dim)
v = FieldVariable('v', 'test', field_u, mesh.dim,
                  primary_var_name='u')

lam = 10.0 # Lame parameters.
mu = 5.0
te = 0.5 # Thermal expansion coefficient.
T0 = 20.0 # Background temperature.
eye_sym = np.array([[1], [1], [0]],
                   dtype=np.float64)
m = Material('m', lam=lam, mu=mu,
             alpha=te * eye_sym)

t2 = FieldVariable('t', 'parameter', field_t, 1,
                   primary_var_name='(set-to-None)')
t2.set_data(t() - T0)

term1 = Term.new('dw_lin_elastic_iso(m.lam, m.mu, v, u)',
                 integral, omega, m=m, v=v, u=u)
term2 = Term.new('dw_biot(m.alpha, v, t)',
                 integral, omega, m=m, v=v, t=t2)
eq = Equation('temperature', term1 - term2)
eqs = Equations([eq])

u_bottom = EssentialBC('u_bottom',
                       bottom, {'u.all' : 0.0})
u_top = EssentialBC('u_top',
                    top, {'u.[0]' : 0.0})

pb.set_equations_instance(eqs, keep_solvers=True)
pb.time_update(ebcs=Conditions([u_bottom, u_top]))

displacement = pb.solve()
out.update(displacement.create_output_dict())

pb.save_state('thermoelasticity.vtk', out=out)

view = Viewer('thermoelasticity.vtk')
view(vector_mode='warp_norm',
     rel_scaling=1, is_scalar_bar=True,
     is_wireframe=True,
     opacity={'wireframe' : 0.1})
