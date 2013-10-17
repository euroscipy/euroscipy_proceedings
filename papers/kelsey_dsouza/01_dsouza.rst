:author: Kelsey D'Souza
:email: kelsey@dsouzaville.com
:institution: Senior at Westwood High School


-----------------------------------------------------------
PySTEMM: Executable Concept Modeling for K-12 STEM Learning
-----------------------------------------------------------

.. !!! TODO: search for "TODO"s in this document!!!
.. TODO: all figure refs

.. class:: abstract

    Although modeling is central to the STEM disciplines (Science, Technology, Engineering, and Math), is is not taught much in K-12 education in the US. In this paper we describe modeling of STEM concepts using executable concept models in Python. The approach applies to all STEM areas and supports learning with pictures, narrative, animation, graph plots, and both bottom-up and top-down modeling. Models can extend other models, making it easy to get started. Incidental complexity and code debugging are reduced by using immutable objects and pure functions. We describe a proof-of-concept tool called PySTEMM and sample models covering topics in math, physics, chemistry, and engineering.

.. class:: keywords

    STEM education, concept models, pure functions

Introduction
============

A *model* is a simplified representation of part of some world, focusing on selected aspects while ignoring others. A model underlies *every* scientific theory, and models are central to all STEM areas — science, technology, engineering, and mathematics — helping us conceptualize, understand, explain, and predict phenomena in an objective way. As part of childhood learning and exploration, we intuitively form mental models, and create physical models in childhood play. Scientists use laboratory-grown biological tissue as a model of human organs. Computational modeling has revolutionized science and engineering, and the 2013 Nobel Price in Chemistry was awarded for computational modeling of biochemical systems. 

.. TODO: reasons to model

Previous research [Whi93], [Orn08] has shown significant learning benefits when model-building and exploring is included in STEM education. Unfortunately, STEM education through middle and high school in the US teaches very little about modeling, and students rarely create or explore models. Students should learn to explore, refute, validate, and change models, and use models to better understand the deep connections across subject areas. Instead, standardized curricula too often sidestep chances to immerse students in ideas of science and maths to make room for more mechanical testing and  drills. In this paper I demonstrate that executable concept models, based on using immutable objects and pure functions in Python:

-  apply across multiple STEM areas,
-  support different representations and learning modes,
-  are quite feasible and approachable,
-  invite bottom-up exploration and assembly, and
-  can help build deep understanding of underlying concepts.


Executable Concept Models
-------------------------

A *concept model* describes things in some world, capturing relevant concepts, attributes, and rules about those attributes. A *concept instance* is a specific individual of a *concept type* e.g. ``NO2`` is a concept instance of the general concept type ``Molecule``. The *concept type* ``Molecule`` might define a ``formula`` attribute for any molecule *instance* to list how many atoms of each element it contains. The *concept instance* ``NO2`` has 1 Nitrogen atom and 2 Oxygen atoms. 

You choose concepts and attributes based on the things you want to focus on. A very different model of a molecule might describe it in terms of functional groups larger than atoms, bonds between groups, sites at which other molecules can interact with it, the geometry of those sites, and the forces that govern interactions at those sites.

An *executable concept model* is represented on a computer, so concept instances and concept types and be manipulated and checked by the machine, increasing confidence in the model. 

PySTEMM Models
--------------

.. TODO: Big-picture "Hybrid-Reality" cycle Models <-> Observations

PySTEMM executable concept models have three parts:

1. *Structure:* A concept type is defined by a Python *class* including attributes and their types, which can reference other concept types; a concept instance is a Python object instantiated from that class, with values for it's attributes.
2. *Functions:* The pure functions that represent additional properties or rules on concept instances are defined as Python *methods* on the class. 
3. *Visualization:* The visualization of the concept type and its instances are defined with Python *dictionaries* used as templates.

.. TODO: a small PySTEMM example with all 3 parts

“Executable” typically implies programming language complexity, debugging headaches, and distractions from the actual concepts under study. By using only immutable objects and pure functions in PySTEMM models, and providing multiple  visualizations, we reduce debugging issues and needless complexity. An immutable object is one whose attribute values do not get modified by the model code. A pure function is one that produces a result without modifying any other attributes or variables, and that result depends solely on its inputs [#]_.

.. [#] Since we use methods on a class for functions, in ``a.f(x)`` the inputs to ``f`` include the argument ``x``, as well as the object ``a`` on which the method was invoked.


The rest of this paper presents a series of models covering math, chemistry, physics, and engineering, introducing key aspects of PySTEMM, and showing the Python model source code as well as the multiple representations generated by PySTEMM. The last section will briefly describe the implementation of PySTEMM.



Mathematics
===========

We begin with models of math functions, then move on to *high-order functions* i.e. functions which accept functions as inputs, or whose result is itself a function. 


Basic Numeric Functions
-----------------------

We model the domain of a function as an attribute ``domain`` which is a list of integers, and the evaluation of a function as a method ``eval(x)``. We model two kinds of functions: ``RuleFunctions`` are functions whose value is defined by a Python expression, and ``TableFunctions`` are functions whose value is defined by a list of ``(x,y)`` pairs. The model in Python defining the *concept types* is:

.. code-block:: python
   :linenos:

    # file: function_types.py

    class Function(Concept):
      domain = Property(List(Int))
      class_template = {K.gradient_color: 'Green'}

    class TableFunction(Function):
      points = List(Tuple(Int, Int))
      domain = Property(List(Int))

      def _get_domain(self):
        return [x for x, y in self.points]

      def eval(self, x):
        for (x1, y1) in self.points:
          if x == x1:
            return y1

      class_template = {K.gradient_color: 'Maroon'}
      instance_template = {K.name: 'Circle'}

    class RuleFunction(Function):
      rule = Callable
      domain = List(Int)

      def eval(self, x):
        return self.rule(x)

      class_template = {K.gradient_color: 'Yellow'}

The ``class_template`` is a dictionary of visualization properties for the concept type, and ``instance_template`` is for visualizing instances. PySTEMM generates the visualization in Figure :ref:`functypes` of these concept types, including the English narrative description:

.. figure:: func1_types.png

    Three ``Function`` concept types.

.. TODO: add keys to most diagrams

We extend this model to explore some concept instances, with the following Python code and corresponding PySTEMM visualization in Figure :ref:`funcinstances`:

.. code-block:: python
   :linenos:

    # file function_instances.py
    from function_types.py import *

    tf = TableFunction(points=[(1, 10), (2, 15)])

    M = Model()
    M.addInstances(tf)
    M.showMethod(tf, 'eval')
    M.showEval(tf,'eval',[1])

.. figure:: func1_instances.png

    ``TableFunction`` concept instance. :label:`funcinstances`

.. TODO: try out M.tf = TableFunction(...) ??

Note that ``tf``, the instance of ``TableFunction``, is shown as a circle in the same color as the ``TableFunction`` class [#]_. Its ``domain`` was calculated from its list of ``points``. ``tf`` evaluates to ``10`` at x=1, and the code for ``eval()`` is shown in the context of the instance. Since ``eval`` is a *pure function*, ``tf.eval(1)`` depends solely on the input ``1`` and the definition of ``tf`` itself, so it is easy to understand the source code.

.. [#] The instance template is merged with the class template to decide how the instance is visualized.

In subsequent sections we elide Python code and show what PySTEMM generates.


Inverse Functions
-----------------

An ``InverseFunction`` inverts another function e.g. :math:`g = f^{-1}`. The model below extends the ``function_instances`` model. The ``InverseFunction(...)`` constructor is a *high-order function* corresponding to the inversion :math:`f^{-1}` operator, since it receives a function to invert, and results in the new inverted function.  

.. code-block:: python
    :linenos:

    from function_instances import *

    class InverseFunction(Concept): ...

    inv = InverseFunction(inverts=tf)

    M.addClasses(InverseFunction)
    M.addInstances(inv)
    M.showEval(inv, 'eval',[15])


The instance visualization generated by PySTEMM in Figure :ref:`funcinverse` shows the inverse function as a blue square, its ``eval()`` effectively flips the ``(x,y)`` pairs of the function it inverts, and its ``domain`` is computed as the set of ``y`` values of the function it inverts.

.. figure:: func_inverse.png

    ``InverseFunction`` concept instance. :label:`funcinverse`


Graph Transforms as High-Order Functions
----------------------------------------

.. figure:: func_bump.png

    Function Tranforms: A ``Bump`` of a ``Shift`` of :math:`x^{2}`. :label:`funcbump`

The graph transformations taught in middle school — translation, scaling,  rotation — are modeled as functions that operate on other functions, producing a transformed function. In the example in Figure :ref:`funcbump`, PySTEMM generates a graph plot of the original function, a shifted version of that function, and a “bumped” version of the shifted function. The instances are defined below:

.. code-block:: python

  Bump(function=
        ShiftX(function=RuleFunc(rule=square),
                by=3),
       start=0, end=5, val=100)

The *limit* of a function is a high-order function: it operates on another function and a target point, and evaluates to a single numeric value (if the limit exists). More advanced operations, such as *differentiation* and *integration*, can also be modeled as high-order functions: they operate on a given function, and result in a new function.

.. TODO: show math & Model for limit, derivative, etc. 
.. TODO: der(f)=def fun(x): return slope(f,x)



Chemistry: Reaction
===================

.. figure:: reaction_types.png

    Reaction Concept Type. :label:`reactiontypes`

An Element is modeled as just a name, since our example model ignores things like electron or nuclear structure. We use a very simple model of a ``Molecule``: a ``formula`` attribute with a list of pairs of element with a number indicating how many atoms of that element. A ``Reaction`` has reactants and products, each being some quantity of a certain kind of molecule. Below is the model of the *concept types* in Python, and Figure :ref:`reactiontypes` as visualized by PySTEMM. Note that convenient Python constructs, like *lists* of *tuples*, are visualized in a correspondingly convenient manner.

.. code-block:: python

    class Element(Concept):
      name = String

    class Molecule(Concept):
      formula = List(Tuple(Element, Int))

    class Reaction(Concept):
      products = List(Tuple(Int, Molecule))
      reactants = List(Tuple(Int, Molecule))

.. figure:: molecule_instance.png

    An Instance of a Molecule. :label:`moleculeinstance`

Figure :ref:`moleculeinstance` shows an instance of a molecule:

.. figure:: reaction_instance.png

    An Instance of a Reaction. :label:`reactioninstance`


And Figure :ref:`reactioninstance` shows an instance of a reaction, visualizing molecules with a computed label for the reaction and for the molecules, and hiding the structure within molecules.


Chemistry: Reaction Balancing
-----------------------------

Our next model will compute reaction balancing for basic chemical reactions. We start with a model of an unbalanced reaction: it just has a list ``ins`` of input molecules, and a list ``outs`` of output molecules, without any coefficients.

.. TODO: show Math version of matrix math

We formulate the reaction-balancing problem as an *integer-linear programming* problem [Sen06]_, which we solve for the molecule coefficients. The reaction ``ins`` and ``outs`` impose a set of constraints on the coefficients: the number of atoms of every element has to balance. The function ``elem_balance_matrix`` computes a matrix of *molecule* vs. *element*, showing the number of
atoms of each element in each molecule, with ``+`` for reactants and ``-`` for products. This matrix multiplied by the vector of solution coefficients must result in all ``0``s. Additionally, all coefficients have to be positive integers, and the ``objective_function`` specifies finding the smallest coefficients that satisfy these constraints.

.. figure:: reaction_balance.png

    Reaction balance matrix and solved coefficients. :label:`balancing`

PySTEMM generates Figure `balancing`, showing the balancing coefficients for an initially unbalanced reaction, and also displaying the values of the ``elem_balance_matrix`` and other intermediate variables.



Chemistry: Layered Models
-------------------------

The previous example illustrates an important advantage of PySTEMM concept modeling. We do not directly jump in and try to model the mathematics of reaction balancing. Instead, the focus is on the structure of the concept instances e.g. What is the model structure for molecules? For reactions?

Once we have a this represented, we decide what the mathematics should be, based on that structure. The math version of a molecule is simply a single column of numbers: how many of each element type in that molecule. The math for a reaction collates these columns into a matrix, with one column for each molecule. It is a relatively simple task to write functions that traverse the concept instances and their attributes, and build up the
corresponding math models (matrices of numbers, in this example).

.. figure:: concept_to_math.png

    Layered concept models and generated Math

Below is the initial model for a reaction network, in Python code, and as visualized by PySTEMM including *instance-level* English narrative. This model does not include any network-level math models.

.. code-block:: python

    class Network(Concept):
      reactions = List(Reaction)

    R1 = Reaction(reactants=[(2, NO2)],
                  products=[(1, NO3), (1, NO)])

    R2 = Reaction(reactants=[(1, NO3), (1, CO)],
                  products=[(1, NO2), (1, CO2)])

    Net = Network(reactions=[R1, R2])

.. figure:: reaction_network.png

    A reaction network with two reactions




Physics
=======

We model the motion of a ball in 2-dimensions under forces. The ball has vector-valued attributes for initial position, velocity, and forces. It also has functions ``acceleration``, ``velocity``, and ``position``, as pure functions of time, using Numpy for numerical integration. PySTEMM generates visualizations that include graphing of the time-varying functions, and animating the position and velocity (vectors) of the ball over time (Figure :ref:`phyfig`).

Like all the other visualizations, the animation is specified by a *template*: dictionaries of visual properties, except that these property values can now be *functions* of both the *object* being animated, and the *time* at which its attributes values should be computed, to determine the visual property values.

.. code-block:: python

    class Ball(Concept):
      forces = List(vector)
      mass, p0, v0 = Float, Instance(vector), ...
      def net_force(self):
        return sum(lambda a, b: a + b, self.forces....))

      def position(self, time):
        return self.p0 + integrate_vec(self.velocity....)

      def p_x(self, time): ....      
      def p_y(self, time): ....

    b = Ball(p0=..., v0=..., mass=..., forces=...)
    m = Model(b)
    m.showGraph(b, 'p_y', (0,10) )
    m.animate(b,    
        (0,10),
        [{k.origin: lambda b,t: [b.p_x(t), b.p_y(t)]]},
         {k.new: k.line, point_list=lambda b, t: ....},
         {k.new: k.line, point_list=lambda b, t: ....}] )

.. figure:: physics_graph.png
    :align: center
    :scale: 40%
    :figclass: w

    Ball in motion as functions of time: graphs, integration, animation :label:`phyfig`



Engineering
===========

In summer 2012 I attended the Ocean Engineering Experience program at MIT, where we designed and built a marine remote-operated vehicle (ROV), constructed primarily out of sealed PVC pipes. In spring 2013, I used PySTEMM to re-do some of the 3-D modeling, and generate some engineering calculations and 3-D visualizations from the model. Here too the models were defined in a pure functional style e.g. to create a number of pipes positioned and sized relatively to each other, the model uses pure functions like ``shift`` and ``rotate`` that take a ``PVCPipe`` and some geometry transform, and return a new ``PVCPipe`` with transformed geometry. This makes it simple to do parametric modeling and construct and try out different ``ROV`` structures. The models shown here are simplified and do not include the motors and the micro-controller assembly.

.. code-block:: python

    class PVCPipe(Concept):
      density = Float
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

The 3-D visualization, including some of the computed engineering attributes.

.. figure:: PastedGraphic.pdf

    ROV made of PVCPipes



Implementation
==============

The overall architecture of PySTEMM is illustrated in Figure :ref:`archfig`, and consists of two main parts: the *tool*, and the *model library*. The tool is implemented with 3 primary classes:

- ``Concept``: a superclass that triggers special handling of the concept class being defined by the *traits* module.
- ``Model``: a collection of concepts classes and concept instances.
- ``View``: an interface to a desktop scriptable drawing application (via AppleScript).


The diagram below explains the operation of PySTEMM in some more detail, and lists external modules that were used for specific purposes.

.. figure:: architecture.png
    :align: center
    :scale: 40%
    :figclass: w

    Architecture of PySTEMM. :label:`archfig`


By requiring all models to be built consistently with objects and pure functions, we gain several benefits:

-  The user models can be manipulated by the tool more easily, to provide tool capabilities like animation and graph-plotting.
-  The values of intermediate values and other computed attributes can be as easily displayed as any stored attributes.
-  Debugging becomes less of an issue, as the models are very close to the math taught in schools for physics, chemistry, etc.

.. TODO: Choice of Python & Why

Templates
---------

All visualization is defined by *templates*, such as the one below:

.. code-block:: python

    Concept_Template = {
      K.text: lambda concept: classLabel(concept),
      K.name: 'Rectangle',
      K.corner_radius: 6,
      ...
      K.gradient_color: "Snow"}

The primary operation on a template is to *apply* it to some modeling object, typically a concept class, or a concept instance. The ``apply_template`` method is:

.. code-block:: python

    def apply_template(t, obj):
      # values are OG values or functions
      # obj: any object, passed into template functions
      # returns: copy of t, functions F replaced by F(obj)
      if isinstance(t, dict):
        return {k: apply_template(v, obj, time)
                   for k, v in t.items()}
      if isinstance(t, list):
        return [apply_template(x, obj, time)
                   for x in t]
      if callable(t):
        return t(obj)
      return t

Animation Templates have some special case handling (not shown here) since their functions take 2 parameters: the *instance* to be rendered, and the value of *time* at which to render its attributes.



Summary
=======

I have described PySTEMM, a tool, model library, and approach for building executable concept models for a variety of STEM subjects. Potential extensions include:

-  Making the models more directly interactive: the main challenge here is that rendering is done via scripting of a desktop application, making such interaction difficult.
-  Publication and sharing of models via the web: since the models are defined as Python code, this would depend on Python’s ability to import over the web
-  Making more generic concept models of systems that involve differential equations.



References
==========

.. [Whi93] White, Barbara Y. *ThinkerTools: Causal Models, Conceptual Change, and Science Education*,
        Vol. 10. Berkeley: Taylor & Francis, 1993. Print. Cognition and Instruction.

.. [Orn08] Ornek, Funda. *Models in Science Education: Applications of Models in Learning and Teaching Science*,
        Turkey: International Journal of Environmental & Science Education, 2008. Print.

.. [Edw04] Edwards, Jonathan. *Example Centric Programming*,
        The College of Information Sciences and Technology. The Pennsylvania State University, 2004.

.. [Fun13] "9.8. Functools — Higher-order Functions and Operations on Callable Objects.",
        2013. http://docs.python.org/2/library/functools.html.

.. [Bla07] Blais, Martin. *True Lieberman-style Delegation in Python*, 
        (Python Recipe)." Active State Code. Active State Software Inc, 14 May 2007.

.. [Sen06] Sen, S. K., Hans Agarwal, and Sagar Sen. *Chemical Equation Balancing: An Integer Programming Approach*, 
        S.A.: Elsevier, 2006.

.. [Chu12] Church, Michael, *Functional Programs Rarely Rot*, http://michaelochurch.wordpress.com/2012/12/06/functional-programs-rarely-rot/


