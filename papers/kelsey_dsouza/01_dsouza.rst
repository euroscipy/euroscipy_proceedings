:author: Kelsey D'Souza
:email: kelsey@dsouzaville.com
:institution: Senior at Westwood High School


-----------------------------------------------------------
PySTEMM: Executable Concept Modeling for K-12 STEM Learning
-----------------------------------------------------------

.. !!! TODO: search for "TODO"s in this document!!!
.. TODO: all figure refs

.. TODO; Positive Tone E.G. Functional programming languages ought to play a central role in mathematics education for middle schools (age range: 10-14). After all, functional programming is a form of algebra and programming is a creative activity about problem solving. Introducing it into mathematics courses would make pre-algebra course come alive. If input and output were invisible, students could implement fun simulations, animations, and even interactive and distributed games all while using nothing more than plain mathematics.

.. TODO: Positive Tone Continued: We have implemented this vision with a simple framework for purely functional I/O. Using this framework, students design, implement, and test plain mathematical functions over numbers, booleans, string, and images. Then the framework wires them up to devices and performs all the translation from external information to internal data (and vice versa)---just like every other operating system. Once middle school students are hooked on this form of programming, our curriculum provides a smooth path for them from pre-algebra to freshman courses in college on object-oriented design and theorem proving.

.. class:: abstract

    Modeling should play a central role in K-12 STEM education, where it could make classes much more engaging. A model underlies every scientific theory, and models are central to all the STEM disciplines (Science, Technology, Engineering, Math). This paper describes executable concept modeling of STEM concepts using immutable objects and pure functions in Python. I present examples in math, physics, chemistry, and engineering, built using a proof-of-concept tool called PySTEMM . The approach applies to all STEM areas and supports learning with pictures, narrative, animation, and graph plots. Models can extend each other, simplifying getting started. The functional-programming style reduces incidental complexity and code debugging. 

.. TODO: the "bottom-up and top-down" is not explained in the paper


.. class:: keywords

   STEM education, STEM models, immutable objects, pure functions



Introduction
============

A *model* is a simplified representation of part of some world, focused on selected aspects. A model underlies every scientific theory, and models are central to all STEM areas — science, technology, engineering, and mathematics — helping us conceptualize, understand, explain, and predict phenomena objectively. Children form mental models and physical models during play to understand their world. Scientists use bio-engineered tissue as a model of human organs. Computational modeling is revolutionizing science and engineering, as recognized by the 2013 Nobel Price in Chemistry going for computational modeling of biochemical systems. 

.. TODO: reasons to model

Previous research [Whi93]_, [Orn08]_ has shown significant learning benefits from model-building and exploring in STEM education. Students should create, validate, refute, and use models to better understand deep connections across subject areas, rather than mechanically drilling through problems. In this paper I demonstrate that executable concept modeling, based on using immutable objects and pure functions in Python:

-  applies across multiple STEM areas,
-  supports different representations and learning modes,
-  is feasible and approachable,
-  encourages bottom-up exploration and assembly, and
-  builds deep understanding of underlying concepts.

.. TODO: for Intel etc. check that claims are supported

Executable Concept Models
-------------------------

A *concept model* describes something by capturing relevant concepts, attributes, and rules. A *concept instance* is a specific individual of a *concept type* e.g. ``NO2`` is a concept instance of the general concept type ``Molecule``. The concept type ``Molecule`` might define a ``formula`` attribute for any molecule instance to list how many atoms of each element it contains. The concept instance ``NO2`` has one ``Nitrogen`` and two ``Oxygen`` atoms. This is similar to the idea from object-oriented programming of an object that is an instance of a class.

Concepts and attributes are chosen to suit a purpose. A different model of ``Molecule`` might describe atoms, functional groups, bonds, sites at which other molecules can interact, site geometry, and forces that govern geometry and interactions.

An *executable concept model* is represented on a computer, so concept instances and concept types can be manipulated and checked by the machine, increasing confidence in the model. 

PySTEMM Models
--------------

.. TODO: Big-picture "Hybrid-Reality" cycle Models <-> Observations

“Executable” typically entails programming language complexity, debugging headaches, and distractions from the actual concepts under study. Much of this complexity stems from *imperative programming*, where variables and object attributes are modified as the program executes its procedures. 

*Functional programming* is a good alternative. It uses (a) *immutable objects*, whose attribute values do not get modified by program code; and (b) *pure functions*, producing a result that depends solely on inputs, without modifying any other attributes or variables. 

PySTEMM, by using immutable objects and pure functions, and providing multiple model representations, reduces needless complexity and debugging. It uses the *Python* programming language to define executable concept models that have three parts:

1. Structure: A concept type is defined by a Python *class* that describes attributes together with their types (which can reference other concept types). A concept instance is a Python *object* instantiated from that class, with values for its attributes.
2. Functions: The pure functions that represent additional properties or rules on concept instances are defined as Python *methods* on the class [#]_. 
3. Visualization: The visualization of concept types and instances are defined with Python *dictionaries* of visual properties, used as *templates*.

.. TODO: a small PySTEMM example with all 3 parts

PySTEMM models focus on defining *what terms and concepts mean*, rather than step-by-step instructions about *how to compute*. PySTEMM functions manipulate not just numbers, but molecules, rigid bodies, planets, visualizations, and even concept types and functions. 

.. [#] Since we use methods on a class for functions, in "``a.f(x)``" the inputs to ``f`` include argument ``x``, and the object ``a`` on which the method is invoked.

In the rest of this paper I present example models from math, chemistry, physics, and engineering, introduce key aspects of PySTEMM, and show  Python model source code as well as multiple model representations generated by PySTEMM. The last section describes the implementation of PySTEMM.


Mathematics
===========

We begin with models of math functions, because math forms the basis of all other models. Next we move on to *high-order* functions i.e. functions that accept functions as inputs, or whose results are functions. Since our focus in this section is modeling math concepts, we will model math functions as objects. In subsequent sections on physics, chemistry, etc., we will directly use normal Python code for math computations.


Basic Numeric Functions
-----------------------

.. figure:: func_types.pdf

    Three ``Function`` concept types. :label:`functypes`

.. TODO: add keys to most diagrams

The Python model of *concept types* for basic functions is:

.. TODO: explain Property & _get_X

.. code-block:: python
   :linenos:

    # file: function_types.py

    class Function(Concept):
      domain = Property(List(Int))
      def eval(self, x): pass
      class_template = {K.gradient_color: 'Green'}

    class RuleFunction(Function):
      rule = Callable
      domain = List(Int)

      def eval(self, x):
        return self.rule(x)

      class_template = {K.gradient_color: 'Yellow'}

    class TableFunction(Function):
      points = List(Tuple(Int, Int))
      domain = Property(List(Int))

      def _get_domain(self):
        return [x for x, y in self.points]

      def eval(self, x):
        return find(y1 for x1,y1 in self.points 
                      if x1==x)

      class_template = {K.gradient_color: 'Maroon'}
      instance_template = {K.name: 'Circle'}


The concept type ``Function`` is defined as a class (line 3), with an attribute ``domain`` which is a list of integers (line 4). "``Property``" allows ``domain`` to be represented differently for different subclasses of ``Function``. Function evaluation is modeled by method ``eval`` (line 5) whose specifics are deferred to subclasses. The visualization of functions is defined by ``class_template`` (line 6).

We define two subclasses of ``Function``, each with different representations. ``RuleFunctions`` (line 8-15) are defined by an attribute ``rule`` that is a Python *callable* expression, an explicit ``domain``, and  ``eval`` that simply invokes ``rule``. ``TableFunctions`` (line 17-29) are defined by a list of ``(x,y)`` pairs in an attribute ``points``, a ``domain``  computed from ``points`` by ``_get_domain``, and ``eval`` that finds the matching pair in ``points``. The ``class_template`` (lines 15, 28) is a dictionary of visualization properties for the concept type, and ``instance_template`` (line 29) is for visualizing instances. PySTEMM generates the visual and English narrative in Figure :ref:`functypes` for  these concept types.

.. figure:: func_instances.pdf

    ``TableFunction`` concept instance. :label:`funcinstances`

Below, we *extend* this model with a ``TableFunction`` instance ``tf`` with its list of ``points`` (line 4), and customize what the model should visualize:

.. code-block:: python
   :linenos:

    # file function_instances.py
    from function_types.py import *

    tf = TableFunction(points=[(1, 10), (2, 15)])

    M = Model()
    M.addInstances(tf)
    M.showMethod(tf, 'eval')
    M.showEval(tf,'eval',[1])


.. TODO: try out M.tf = TableFunction(...) ??


PySTEMM generates  the visualization in Figure :ref:`funcinstances`. The ``domain`` of ``tf`` was calculated from its ``points``, its value at ``x=1`` is ``10``, and the code for ``eval()`` is shown in the context of the instance. Since ``eval`` is a *pure function*, ``tf.eval(1)`` depends solely on the input ``1`` and the definition of ``tf`` itself, so it is easy to understand the source code: it returns the ``y1`` from the ``x1,y1`` pair that matches the input ``x``.

Note that ``tf`` is drawn as a circle of the same color as the ``TableFunction`` class: the ``instance_template`` for ``TableFunction`` is merged with the ``class_template`` before being applied to ``tf``.


Inverse Functions
-----------------

.. figure:: func_inverse.pdf

    ``InverseFunction`` type and instance. :label:`funcinverse`

An ``InverseFunction`` inverts another: :math:`g = f^{-1}(x)`. The model below extends the ``function_instances`` model with a class and an instance. On line 5, the ``InverseFunction(...)`` constructor is a *high-order function* corresponding to the :math:`f^{-1}` operator, since it receives a function ``tf`` to invert, and produces the new inverted function ``inv``.  

.. code-block:: python
    :linenos:

    from function_instances import *

    class InverseFunction(Concept): ...

    inv = InverseFunction(inverts=tf)

    M.addClasses(InverseFunction)
    M.addInstances(inv)
    M.showEval(inv, 'eval',[15])


The instance visualization generated by PySTEMM in Figure :ref:`funcinverse` shows the inverse function as a blue square, its ``eval()`` effectively flips the ``(x,y)`` pairs of the function it inverts, and its ``domain`` is computed as the set of ``y`` values of the function it inverts.


Graph Transforms and High-Order Functions
-----------------------------------------

.. figure:: shift_bump.pdf
    :align: center
    :scale: 40%
    :figclass: w

    Function Transforms: A ``Bump`` of a ``Shift`` of :math:`x^{2}`. :label:`funcbump`


A graph transformation as taught in middle school — translation, scaling,  rotation — is modeled as a function that operates on a ``source`` function, producing the transformed function. In Figure :ref:`funcbump`, PySTEMM generates a graph plot of the original function, a shifted version, and a “bumped” version of the shifted function. The instances are defined as:

.. TODO: Add intermediate class Transform, flip instance layout R<->L

.. code-block:: python

  Bump(source =
          ShiftX(source = RuleFunc(rule=square),
                 by=3),
       start=0, end=5, val=100)

Similarly, the *limit* of a function is a high-order function: it operates on another function and a target point, and evaluates to a single numeric value. Calculus operators, such as *differentiation* and *integration*, can be modeled as high-order functions as well: they operate on a function and produce a new function.

.. TODO: show math & Model for limit, derivative, etc. 
.. TODO: der(f)=def fun(x): return slope(f,x)



Chemistry: Reaction
===================

.. figure:: reaction_types.pdf

    ``Reaction`` concept type. :label:`reactiontypes`

.. figure:: reaction_instance.pdf

    An instance of ``Reaction``. :label:`reactioninstance`

.. code-block:: python
    :linenos:

    class Element(Concept):
      name = String

    class Molecule(Concept):
      formula = List(Tuple(Element, Int))
      instance_template = {
        K.text: lambda m: computed_label(m)}

    class Reaction(Concept):
      products = List(Tuple(Int, Molecule))
      reactants = List(Tuple(Int, Molecule))

An ``Element`` is modeled as just a name, since we ignore electron and nuclear structure. A ``Molecule`` has an attribute ``formula`` with a list of pairs of element with a number indicating the number of atoms of that element. A ``Reaction`` has ``reactants`` and ``products``, each some quantity of a certain molecule. This Python model is visualized by PySTEMM in Figure :ref:`reactiontypes`. 

Note that convenient Python constructs, like *lists* of *tuples*, are visualized in a similarly convenient manner. Also, the ``instance_template`` for molecule (lines 6-7), specifying the visualization properties for a molecule instance, contains a *function* which takes a molecule instance and computes its label. Visualization templates are parameterized by the objects they will be applied to.

Figure :ref:`reactioninstance` shows an instance of a reaction, showing reaction structure and computed labels for reactions and molecules, while hiding the ``formula`` structure within molecules. 


Reaction Balancing
------------------

.. figure:: reaction_balance.pdf

    ``Reaction`` balance matrix and solved coefficients. :label:`balancing`

Our next model computes reaction balancing for reactions. An unbalanced reaction has lists ``ins`` and ``outs`` of  molecules without coefficients. Figure :ref:`balancing` shows how PySTEMM visualizes a reaction with the ``balance`` computation, coefficients, and intermediate values, as explained below.

.. TODO: show Math version of matrix math
.. TODO: why I chose ILP formulation

We formulate reaction-balancing as an *integer-linear programming* problem [Sen06]_, which we solve for molecule coefficients. The ``formula`` of the  molecules constrain the coefficients, since atoms of every element must balance. The function ``elem_balance_matrix`` computes a matrix of *molecule* vs. *element*, with the number of atoms of each element in each molecule, with ``+`` for ``ins`` and ``-`` for ``outs``. This matrix multiplied by the vector of coefficients must result in all ``0``. All coefficients have to be positive integers (``diagonal_matrix``), and the ``objective_function`` seeks the smallest coefficients  satisfying these constraints.


Once we have balanced reactions, we can add attributes and functions to model reaction stoichiometry and thermodynamics. For example:

.. code-block:: python

    class Element(Concept):
      name = String
      atomic_mass = Float

    class Molecule(Concept):
      formula = List(Tuple(Element, Int))
      molar_mass = Property(Float)
      def _get_molar_mass(self):
        return sum([n * el.atomic_mass 
                      for el, n in self.formula])

    Fe = Element(name='Fe', atomic_mass=56)
    Cl = Element(name='Cl', atomic_mass=35.5)
    FeCl2 = Molecule(formula=[(Fe,1), (Cl,2)])

    FeCl2.molar_mass # = 127

.. TODO: can load from standard chemistry data e.g. CSV, XML, JSON

Reaction Network
----------------

.. code-block:: python

    class Network(Concept):
      reactions = List(Reaction)

    R1 = Reaction(reactants=[(2, NO2)],
                  products=[(1, NO3), (1, NO)])

    R2 = Reaction(reactants=[(1, NO3), (1, CO)],
                  products=[(1, NO2), (1, CO2)])

    Net = Network(reactions=[R1, R2])

.. figure:: reaction_network.pdf

    A reaction ``Network`` with two reactions. :label:`network`

A ``Network`` of coupled chemical reactions has a list of ``reactions``. Given this Python model, and a narrative template for ``Reaction``, PySTEMM generates Figure :ref:`network`, including the *instance-level* English narrative. Just as there are element balance constraints on an individual reaction, we could model network-level constraints on the reaction rates and concentrations of chemical species, but have not shown this here.


Layered Models
--------------

.. figure:: concept_to_math.pdf
    :scale: 65%

    Layered concept models and generated math.

The reaction examples illustrate an important advantage of PySTEMM  modeling; instead of directly modeling the mathematics of reaction, we focus on the structure of the concept instances; in this case, what constitutes a molecule, or a reaction?

From this model, we compute the math model. The math version of a molecule is a single column with the number of atoms of each element type in that molecule. The math for a reaction collects this column from each molecule and combines them into an ``element_balance_matrix``. Pure functions thus  easily traverse the concept instances to build corresponding math models such as matrices of numbers.


Physics
=======

.. figure:: physics_graph_n_animation.pdf
    :align: center
    :scale: 40%
    :figclass: w

    ``Ball`` in motion: functions of time as code, graphs, animation :label:`phyfig`


Below is a model of the motion of a ball under constant force. The ball has vector-valued attributes for initial position, velocity, and forces (lines 2,3). The functions ``acceleration``, ``velocity``, and ``position`` are pure functions of time and use numerical integration. We visualize ball ``b`` via ``showGraph`` and ``animate`` (lines 18-19). Like all visualizations, the animation is specified by a *template* (line 21): a dictionary of visual properties, except that these properties can be *functions* of the *object* being animated, and the *time* at which its attributes values are computed.


.. code-block:: python
    :linenos:

    class Ball(Concept):
      mass, p0, v0 = Float, Instance(vector), ...
      forces = List(vector)
      def net_force(self):
        return v_sum(self.forces)
      def acceleration(self, time):
        return self.net_force() / self.mass
      def velocity(self, time):
        return self.v0 + v_integrate(self.acceleration, time)
      def position(self, time):
        return self.p0 + v_integrate(self.velocity, time)

      def p_x(self, time): ....      
      def p_y(self, time): ....

    b = Ball(p0=..., v0=..., mass=..., forces=...)
    m = Model(b)
    m.showGraph(b, ('a_y','v_y','p_y'), (0,10))
    m.animate(b,    
        (0,10),
        [{K.new: K.shape,
          K.origin: lambda b,t: [b.p_x(t), b.p_y(t)]]},
         {K.new: K.line, point_list=lambda b,t: ...},
         {K.new: K.line, point_list=lambda b,t: ...}] )


PySTEMM generates graphs of the time-varying functions, and a 2-D animation of the position and velocity vectors of the ball over time (Figure :ref:`phyfig`). 


Engineering
===========

.. figure:: rov.pdf
    :scale: 50%

    ``ROV`` made of ``PVCPipes``. :label:`rovfig`

In Summer 2012 I attended the OEX program at MIT, where we designed and built a marine remote-operated vehicle (ROV) with sensors to monitor water conditions. I later used PySTEMM to recreate models of the ROV, and generate engineering attributes and 3-D visualizations like Figure :ref:`rovfig`. 

The ``ROV`` is built from ``PVCPipes`` in a functional style. To create several ``PVCPipes`` positioned and sized relative to each other, the model uses pure functions like ``shift`` and ``rotate`` that take a ``PVCPipe`` and some geometry, and produce a transformed ``PVCPipe``. This makes it simple to define parametric models and rapidly try different ``ROV`` structures. The model shown excludes motors, micro-controller, and computed drag, net force, and torque.

.. code-block:: python

    class PVCPipe(Concept):
      length, radius, density = Float, Float, Float
      def shift(self, v): 
        return PVCPipe(self.p0 + v, self.r, self.axis)
      def rotate(self, a):
        return PVCPipe(self.p0, self.r, self.axis + a)

    class ROV(Concept):
      body = List(PVCPipe)
      def mass(self): ...
      def center_of_mass(self): ...
      def moment_of_inertia(self): ...

    p1 = PVCPipe(....)
    p2 = p1.shift((0,0,3), ...)
    c1, c2 = p1.rotate((0,0,90))...
    rov = ROV(body=p1, p2, c1, c2)

.. TODO: diagram showing a sequence of Pipe-transforms

.. TODO: view: X as: Y via: Map, called "view" because analogous to template
.. TODO: @rule example as table: Concept Type, Valid/Invalid Instance, Valid/Invalid Observation

Implementation
==============

Architecture
------------

The overall architecture of PySTEMM, illustrated in Figure :ref:`archfig`, has two main parts: *Tool* and *Model Library*. The *tool* manipulates *models*, traversing them at the type and instance level and generating visualizations. The *tool* is implemented with 3 classes:

- ``Concept``: a superclass that triggers special handling of the concept type to process attribute-type definitions.
- ``Model``: a collection of concepts classes and concept instances, configured with some visualization.
- ``View``: an interface to a drawing application scripted via AppleScript.

The *model library* includes the models presented in this paper and any additional models any PySTEMM user would create. Figure :ref:`archfig` explains the architecture in more detail, and lists external modules that were used for specific purposes. Attribute type definitions and initialization use the Traits module [Tra14]_.

.. TODO: remove "Loose & Hybrid Model"

.. figure:: architecture.pdf
    :align: center
    :scale: 40%
    :figclass: w

    Architecture of PySTEMM. :label:`archfig`


We gain several benefits by building models with immutable objects and pure functions:

-  The *user models* can be manipulated by the *tool* more easily to provide tool capabilities like animation and graph-plotting, based on evaluating pure functions at different points in time.
-  The values of computed attributes and other intermediate values can be visualized as easily and unambiguously as any stored attributes.
-  Debugging becomes much less of an issue since values do not change while executing a model, and the definitions parallel the math taught in school science.

The source code for PySTEMM is available at github.com/kdz/pystemm.


.. TODO: Choice of Python & Why

Python
------

Python provides many advantages to this project:

- adequate support for high-order functions and functional programming; 
- lightweight and flexible syntax, with convenient modeling constructs like lists, tuples, and dictionaries; 
- good facilities to manipulate classes, methods, and source code; 
- vast ecosystem of open-source libraries, including excellent ones for scientific computing.


Templates
---------

All visualization is defined by *templates* containing visual property values, or functions to compute those values:

.. code-block:: python

    Concept_Template = {
      K.text: lambda concept: computeClassLabel(concept),
      K.name: 'Rectangle',
      K.corner_radius: 6,
      ...
      K.gradient_color: "Snow"}

The primary operation on a template is to *apply* it to some modeling object, typically a concept class or instance:

.. code-block:: python

    def apply_template(t, obj, time=None):
      # t.values are drawing-app values, or functions
      # obj: any object, passed into template functions
      # returns copy of t, F(obj) replaces functions F
      if isinstance(t, dict):
        return {k: apply_template(v, obj, time)
                   for k, v in t.items()}
      if isinstance(t, list):
        return [apply_template(x, obj, time)
                   for x in t]
      if callable(t):
        return t(obj) if arity(t)==1 else t(obj, time)
      return t

Animation templates have special case handling, since their functions take two parameters: the *instance* to be rendered, and the *time* at which to render its attributes.

Templates can also be *merged*. Figure :ref:`funcinstances` shows an  instance of ``TableFunction`` as a circle in the same color as the ``TableFunction`` class, by merging an ``instance_template`` with a ``class_template``.


Summary
=======

I have described PySTEMM as a tool, model library, and approach for building executable concept models for a variety of STEM subjects. The PySTEMM approach, using immutable objects and pure functions in Python, can apply to all STEM areas. It supports learning through pictures, narrative, animation, and graph plots, all generated from a single model definition, with minimal incidental complexity and code debugging issues. Such modeling, if given a more central role in K-12 STEM education, could make STEM learning much more deeply engaging. 


.. TODO: extension: interactive models, tiled interface, web publish, differential equations, symbolic with sympy.

.. TODO: tangible, "play", other sales points
.. TODO: add short indented italized discussion of highlights

.. TODO: TOC: Models(Math,Chem,Phy,Eng,@rule), Obser(JSON,Image,@rule,@within), TileBrowser, Implementation


References
==========

.. [Whi93] White, Barbara Y. “ThinkerTools: Causal Models, Conceptual Change, and Science Education”, Cognition and Instruction, Vol. 10, No. 1.

.. [Orn08] Ornek, Funda. “Models in Science Education: Applications of Models in Learning and Teaching Science”, International Journal of Environmental & Science Education, 2008.

.. [Edw04] Edwards, Jonathan. “Example Centric Programming”, The College of Information Sciences and Technology (Pennsylvania State University: 2004), http://www.subtext-lang.org/OOPSLA04.pdf

.. [Fun13] "9.8. Functools — Higher-order Functions and Operations on Callable Objects.",  Python Software Foundation, 2013. http://docs.python.org/2/library/functools.html.

.. [Bla07] Blais, Martin. “True Lieberman-style Delegation in Python." Active State Software, 2007, http://code.activestate.com/recipes/519639-true-lieberman-style-delegation-in-python/.

.. [Sen06] Sen, S. K., Hans Agarwal, and Sagar Sen. “Chemical Equation Balancing: An Integer Programming Approach”, Mathematical and Computer Modeling, Vol. 44, No.7-8, 2006.

.. [Tra14] Enthought Traits Library, http://code.enthought.com/projects/traits/


.. TODO: add concord.org, euroscipy

