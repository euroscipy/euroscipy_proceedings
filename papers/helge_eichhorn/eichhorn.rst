:author: Helge Eichhorn
:email: eichhorn@dik.tu-darmstadt.de
:institution: Technische Universität Darmstadt, Department of Computer Integrated Design

:author: Reiner Anderl
:email: anderl@dik.tu-darmstadt.de
:institution: Technische Universität Darmstadt, Department of Computer Integrated Design

--------------------------------------------------
Plyades: A Python Library for Space Mission Design
--------------------------------------------------

.. class:: abstract

    TODO
    Designing a space mission is a computation-heavy task.
    Software tools that conduct the necessary numerical simulations and optimizations are therefore indispensable.
    Since the beginning of computational astrodynamics the language of choice has been Fortran and more recently MATLAB.
    This talk explores how Python's unique strengths and its ecosystem make it a viable alternative for future missions.

.. class:: keywords

   data modeling, object-oriented programming, orbital mechanics, astrodynamics

Introduction
------------

Designing a space mission trajectory is a computation-heavy task.
Software tools that conduct the necessary numerical simulations and optimizations are therefore indispensable.
Due to the high numerical performance requirements Fortran remains the top language of choice.
Since no mission or spacecraft is alike the ever-changing requirements and constraints demand high development speed and programmer productivity.
Fortran's idiosyncracies and compiled nature on the other hand are not helpful in this regard.
This has led to high popularity of the MATLAB programming environment in the astrodynamics community.
While it possible to connect Fortran and MATLAB through the MEX interface it is a classical example of the "two-language-problem" with its well known issues and complexities.
Another problem is the fact that both MATLAB and most Fortran compilers are propietary and cannot be used easily for educating the next generation of space mission analysts.

This presentation explores how the unique strengths of the Python language and the Scientific Python ecosystem (Cython, Numba, etc.) make it a compelling alternative to the traditional Fortran/MATLAB mix.
Pythonic solutions to classical astrodynamics problems like the calculation of the classical orbital elements, the solution of the Kepler problem and the numerical propagation and optimization of trajectories will be demonstrated.
These are generated with the speaker's Plyades library which builds on Numpy, SciPy, Matplotlib, Astropy, and others to enable rapid prototyping of analyses and visualizations.
The talk concludes with a comparison of Python to other old and new languages that have been considered to complement or supplant Fortran, e.g.
C++, Java, Julia.
blabla Orekit [Ore15]_ schorger.
 
Requirements for the Plyades Library
------------------------------------

Within the following requirements the keywords *shall*, *should*, and *may* are to be interpreted as specified in ISO 29148 [ISO11]_.

The library should be written in pure Python.
Cython shall be the 
All low-level functionality shall be based on pure functions.
The library shall be able to use SPICE kernels to compute ephemerides of celestial bodies.
Each object shall provide commonly used visualizations as instance methods.

Schmarrn

Design of the Plyades Object Model
----------------------------------

The Body Class
~~~~~~~~~~~~~~

The Body class is a simple helper class that holds physical constants and other properties of celestial bodies such as planets and moon.
These include

* the name of the body
* the gravitational parameter :math:`\mu`
* the mean radius :math:`r_m`
* the equatorial radius :math:`r_e`
* the polar radius :math:`r_p`
* the :math:`J_2` coefficient of the bodies gravity potential
* and the identification code used within the JPL ephemrides.

The State Class
~~~~~~~~~~~~~~~

The Orbit Class
~~~~~~~~~~~~~~~

The Orbit class is a simple helper class

Exemplary Usage
---------------

In this example we use the Plyades library to conduct an analysis of the orbit of the International Space Station (ISS) [#]_.
We obtain the inital state data on August 28, 2015, 12:00h from NASA realtime trajectory data [NAS15]_ and  use it to instantiate a Plyades ``State`` object as shown below.

.. [#] A Jupyter Notebook with with this analysis can be obtained from `Github <https://github.com/helgee/euroscipy-2015>`_.

.. code-block:: python

    iss_r = np.array([
        -2775.03475,
        4524.24941,
        4207.43331,
        ]) * astropy.units.km
    iss_v = np.array([
        -3.641793088,
        -5.665088604,
        3.679500667,
        ]) * astropy.units.km/units.s
    iss_t = astropy.time.Time('2015-08-28T12:00:00.000')
    frame = 'ECI'
    body = plyades.bodies.EARTH

    iss = plyades.State(iss_r, iss_v, iss_t, frame, body)

The position (``iss_r``) and velocity (``iss_v``) vectors use the functionality units from the Astropy package [ASP13]_ while the timestamp (``iss_t``) is an AstroPy ``Time`` object.
The constant ``EARTH`` from the ``plyades.bodies`` module is a ``Body`` object and provides Earth's planetary constants.

* Semi-major axis: :math:`a=6777.773` km
* Eccentricity: :math:`e=0.00109`
* Inclination: :math:`i=51.724` deg
* Longitude of ascending node: :math:`\Omega=82.803` deg
* Argument of periapsis: :math:`\omega=101.293` deg
* True anomaly: :math:`\nu=48.984` deg

.. code-block:: python

    kepler_orbit = iss.kepler_orbit()
    kepler_orbit.plot3d()

.. figure:: 3d_orbit.png

    A three-dimensional visualization of the orbit based on Matplotlib. :label:`3d`

.. code-block:: python

    newton_orbit = iss.propagate(
        iss.period*1.3,
        max_step=500,
        interpolate=200
    )
    newton_orbit.plot_plane(plane='XZ', show_steps=True)

.. figure:: numerical_orbit.png

    Visualization of a numerically propagated orbit with intermediate solver steps (+, blue), start point (+, red), and end point (x, red). :label:`numerical`

.. code-block:: python

    @iss.gravity
    def newton_j2(f, t, y, params):
        r = np.sqrt(np.square(y[:3]).sum())
        mu = params['body'].mu.value
        j2 = params['body'].j2
        r_m = params['body'].mean_radius.value
        rx, ry, rz = y[:3]
        f[:3] += y[3:]
        pj = -3/2*mu*j2*r_m**2/r**5
        f[3] += -mu*rx/r**3 + pj*rx*(1-5*rz**2/r**2)
        f[4] += -mu*ry/r**3 + pj*ry*(1-5*rz**2/r**2)
        f[5] += -mu*rz/r**3 + pj*rz*(3-5*rz**2/r**2)

.. figure:: perturbed_orbit.png

    Visualization of the perturbed orbit. :label:`perturbed`

.. figure:: osculating_node.png
    :scale: 40%

    Secular perturbation on the longitude of the ascending node. :label:`osculating`

Future Development
------------------

As of this writing Plyades has been superseded by the Python Astrodynamics project [PyA15]_.
The project aims to merge the three MIT-licensed, Python-based astrodynamics libraries Plyades, Poliastro [JCR15]_ and Orbital [FML15]_.

Conclusion
----------

References
----------

.. [Ore15] CS Systèmes d'Information. *Orekit: An accurate and efficient core layer for space flight dynamics applications*,
           http://www.orekit.org, last visited: September 17, 2015.

.. [RCM08] Robert C. Martin. *Clean Code: A Handbook of Agile Software Craftsmanship*, Prentice Hall, 2008.

.. [DAV13] David A. Vallado, Wayne D. McClain. *Fundamentals of Astrodynamics and Applications*, 4th Edition, Microcosm Press, 2013.

.. [HEi15] Helge Eichhorn. *Plyades: A Python astrodynamics library*, http://github.com/helgee/plyades, last visited: September 17, 2015.

.. [PyA15] Juan Luis Cano Rodriguez, Helge Eichhorn, Frazer McLean. *Python Astrodynamics*, http://www.python-astrodynamics.org, last visited: September 17, 2015.

.. [JCR15] Juan Luis Cano Rodríguez, Jorge Cañardo Alastuey. *Poliastro: Astrodynamics in Python*, Zenodo, 2015. `doi:10.5281/zenodo.17462 <http://dx.doi.org/10.5281/zenodo.17462>`_.

.. [FML15] Frazer McLean. *Orbital*, https://github.com/RazerM/orbital, last visited: September 17, 2015.

.. [NAS15] National Aeronautics and Space Association. *ISS Trajectory Data*, http://spaceflight.nasa.gov/realdata/sightings/SSapplications/Post/JavaSSOP/orbit/ISS/SVPOST.html, last visited: August 28, 2015.

.. [ASP13] The Astropy Collaboration. *Astropy: A community Python package for astronomy*, Astronomy & Astrophysics, 558(2013):A33.

.. [ISO11] TODO
