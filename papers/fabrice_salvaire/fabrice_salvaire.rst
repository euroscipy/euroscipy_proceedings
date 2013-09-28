:author: Fabrice Salvaire
:email: fabrice.salvaire@orange.fr
:institution: Genomic Vision SA

.. -------------------------------------------------------------------------------------------------

.. Notes

   HDF5 tools
   unusual way to use a dataset

.. -------------------------------------------------------------------------------------------------

-------------------------------------------
High-Content Digital Microscopy with Python
-------------------------------------------

.. class:: abstract

  High-Content Digital Microscopy open the way for new research and medical diagnostic due to the
  enhancement on user comfort, data storage and throughput. A digital microscopy platform has for
  aim to capture an image of a cover slip, to store the information on file server and database, to
  visualise the image and perform analysis. We will discuss how the Python ecosystem could provide
  efficiently a such software platform.
 
.. class:: keywords

  high-content microscopy, digital microscopy

Introduction
------------

.. Notes
   as well as other 
   was widely used to perform

.. lexicon
  field of view
  tile
  mosaic
  wave length / colour
  sample
  specimen
  virtual slide

Since early times optical microscopy play an important role in biology research and medical
diagnostic. Nowadays digital microscopy is a natural evolution of the technology that provide many
enhancements on user comfort, data storage and throughput. In comparison to binocular microscopy,
monitor vision improves considerably the comfort of the staff. Indeed binocular microscopes cause
severe stress to eyes due to the low light intensity entering in the eyes. An anecdote about this
stress is that many people relate they continue to see fluorescent signal labelling when they go to
sleep. The second kind of enhancement is the benefit of the digitisation of the material to freeze
and store the information for short to long term storage. Most of the original materials need to be
stored at low temperature and in the dark for a maximal period. In comparison digital storage is
able to compress and duplicate easily the information, to protect the data integrity by checksum and
data confidentiality by cryptography. The third enhancement concerns high-content application where
the automation provide a considerable scale-up of the data processing throughput and thus open the
way for new research and medical diagnostic.

Data Acquisition
----------------

.. Now to appreciate the volume of data to acquire, 
   reasoning ?

We will first measure how big are the data and understand why? To reach the required resolution to
see specimen details, optical microscopes use objectives having a magnification up to the
diffraction limit which is about :math:`100\times`. Nowadays the pixel size for a CCD and sCMOS
camera is about 6.5 um, thus at magnification :math:`40\times` we reach a resolution of 162.5 nm. To
continue our reasoning, we will consider a specimen deposited on a cover slip which is a glass
square surface of 18 mm wide. Later we will relate the support and the specimen by the more generic
therm *slide*, which corresponds to a larger glass surface. Consequently to cover this surface at
this magnification we have to acquire an area larger than :math:`100\,000` px wide, thus of the
order of 10 billion of pixels which is roughly 300 times larger than the actual largest professional
digital camera (36 Mpx). In light of foregoing digital microscopy are big data similar to spatial
images and involve a software platform similar to the well known Google Map.

For scientific application, we use preferably monochrome camera so as to avoid the interpolation of
a Bayer mosaic. Instead to capture all the colour spectrum at the same time, colours are captured
sequentially where a filter with the corresponding wave length transmission is placed in front of
the camera. These shots are called colour field of view. Figure :ref:`epifluorescence-microscope`
shows the schematic of an epifluorescence microscope which is an application of this acquisition
method.

.. figure:: figure-microscope.pdf
    :scale: 50%
    :figclass: bht

    Schematic of an epifluorescence microscope where specimens are labelled with fluorescent
    molecules so called fluorophores. In this example we are capturing an image for a fluorophore
    having an excitation wave length in the blue and an emission wave length in the green. The
    filters are used to restrict the excitation and filter the
    emission. :label:`epifluorescence-microscope`

A camera like the Andor Neo sCMOS features a sensor of :math:`2560 \times 2160` px that corresponds
to a surface of :math:`416 \times 351` um. So to cover the whole specimen surface we have to capture
a mosaic of fields of view of size :math:`40 \times 50` (2000 tiles) using an automatised stagger.

The sCMOS Andor Neo camera features a standard amplifier-DAC stage with a 12-bit resolution and
another stage with a combination of two amplifier-DACs to achieve a 16-bit resolution for high
dynamic image. Thus image pixels must be encoded using an unsigned 16-bit integer data type. It
means a colour field of view weights 10 MB and our mosaic 20 GB for one colour.

Depending of the intensity dynamic of the specimen and the zero-padding arising from the DAC, most
of the pixels will have a lot of zeros on the most significant bits. For this reason the amount of
data could be efficiently reduced using a lossless compression in conjunction with a bit shuffling,
so as to group the zeros together and form long zero sequences in the byte stream.

When the specimen is observed with several colours, we have two strategies to acquire the mosaic,
the first one is to acquire a mosaic per colour and the second one is to acquire several colours per
field of view. Both methods have advantages and disadvantages. One of the differences is the
uncertainty that occurs on the registration of the colour fields of view. When we capture several
colour per field of view at the same staging position, the relative positioning error is due to the
optic. While when we capture a mosaic per colour, the error is also due to the reproducibility of
the stagger. The regularity of the mosaic which depends of the step positioning error is always due
to the stagger precision. So as to perform a field of view registration without black zone in the
reconstructed image, we drive the stagger with a sufficient overlapping zone on both
direction. Another irregularity on the field of view mosaic is due to the camera alignment error
according to the stagger axes that draw a sheared mosaic pattern as you can see in figure
:ref:`sheared-mosaic`. The shearing has any serious effect on the reconstructed image since it only
displaces systematically the fields of view in the mosaic frame.

.. figure:: figure-sheared-mosaic.pdf
   :scale: 42%
   :figclass: bht

   Field of View Mosaic showing a sheared effect due to the camera misalignment. The tiles are
   rotated in the stagger frame but not in the mosaic frame. :label:`sheared-mosaic`

All these uncertainties could be studied using fluorescent beads with an appropriate density on the
cover slip and an image registration algorithm.

The third dimension of a specimen could be accessed using the vertical focus axis of the microscope
so as to perform a so called z-stack of images that enlarge the depth of field virtually and could
improve the focus accuracy.

Virtual Slide Format and Storage
--------------------------------

We can now defines the data structure of an acquisition so called later a virtual slide.  A virtual
slide is made of a mosaic of fields of view and a set of attributes that constitute the so called
*slide header*. Examples of attribute are a slide identifier, a date of acquisition or an assay
type.

The mosaic is a set of colour fields of view made of a mosaic index :math:`(r,c)`, a stagger
position :math:`(x,y,z)`, a colour index :math:`w` and an image array of unsigned 16-bit integers.
To store images in memory, the Numpy [Numpy]_ library is well appropriate since it maps efficiently
a C linear array data structure in Python.

.. Notes
   and features like B-Tree indexing and rewriting

From this mosaic of field of views, we can imagine to reconstruct once the slide image and produce a
giant image, where we could use for this purpose the BigTIFF [BigTIFF] extension to the TIFF
format. But if we want to keep raw data without information loss we have to imagine a way to store
the original fields of view and process them on-line. 

The HDF5 [HDF5]_ library and its h5py [h5py]_ Python bindings is perfectly suited for this
purpose. The content of an HDF5 file is self defined and the library is open source which guaranty a
long therm access to the data. The structure of an HDF5 file is similar to a file system having
folder objects so called groups and N-dimensional array objects so called dataset that corresponds
here to files. Each of these objects could have attached attributes. This virtual file system
provides the same flexibility than a real file system similar to an Unix loop device.

.. figure:: figure-hdf5-file-system.pdf
   :scale: 60%
   :figclass: bht

   HDF5 Virtual File System. Attributes could be attached to each node. :label:`hdf5-file-system`

The h5py module provides a Pythonic API and map Numpy arrays to datasets and reciprocally, the following code
snippet gives an overview of its usage:

.. code-block:: python

  import numpy as np
  import h5py
  slide_file = h5py.File('slide.hdf5', 'w')
  slide_file.attrs['slide_name'] = u'John Doe'
  root_group = slide_file['/']
  image_group = root_group.create_group('images')
  n = 1000
  image_dataset = image_group.create_dataset(
    'image1', shape=(100*n, 100*n), dtype=np.uint16)
  data = np.arange(n*n, dtype=np.uint16).reshape((n,n))
  image_dataset[n:2*n,n:2*n] = data

As usual for large data set, the HDF5 library implements a data blocking concept so called
chunk. Indeed the data compression as well the efficiency of the data transfer require dataset to be
splitted in chunks. This feature permits to only read and write a subset of the dataset which is
called an hyperslab. Moreover it provides a way to Python to map concepts such view and
broadcasting. It permits also to implement a read-ahead and cache mechanism to speedup the data
transfer from storage to memory.

Another key feature of the HDF5 library is to implement a modular and powerful data transfer
pipeline (Figure :ref:`hdf5-pipeline`) whose aim is to decompress the data from stored chunks,
scatter-gather the data and transform them, for example to apply a scale-offset filter. The h5py
module provides the classic GZIP compression as well its faster counterpart LZF [LZF]_ and other
compression algorithm could be added easily as plugin.

.. figure:: figure-hdf5-pipeline.pdf
   :scale: 60%
   :figclass: bht

   HDF5 Data Transfer Pipeline. :label:`hdf5-pipeline`

..  as it would be for a TIFF image file

The flexibility of HDF5 permits to use different strategies to store our fields of view according to
our application. The guideline is to think how images will be retrieved and used. For example if we
want to get the field of view as a planar image then we should use the same shape for the dataset,
i.e. if the image shape is :math:`(H,W)` then the dataset shape should be :math:`(N_w*H,W)` where
:math:`N_w` is the number of colour planes. Like this we can map directly the data from storage to
memory. The planar format is usually more suited for analysis purpose, but if we want to privilege
the display then we could choose an interleaved format.

To store the mosaic we could use a dataset per field of view or pack everything in only one dataset
thanks to the data blocking to make this efficient and transparent. For example if the mosaic shape
is :math:`(R,C)` then we could create a dataset of shape :math:`(R*N_w*H,C*W)` with a chunk size of
:math:`(h,w)` where :math:`H = n*h`, :math:`W = n*w` and :math:`n \in \mathbb{Z}^{*+}` (Figure
:ref:`mosaic-dataset`). The induced overhead will be smoothed by the fact the images are stored in
chunks.

.. figure:: figure-dataset.pdf
   :scale: 50%
   :figclass: bht

   A dataset and its chunks for a :math:`2 \times 2` mosaic. :label:`mosaic-dataset`

However if we want to load at the same time a set of consecutive images, then we could use this
linear dataset shape :math:`(R*C*N_w*H,W)` and index the image using the linearised index
:math:`r*W + c` (Figure :ref:`linear-dataset`). For example the code to get the field of view in the
interval :math:`[10,20:30]` would be:

.. code-block:: python

  lower_index = 10*W + 20
  upper_index = 10*W + 30
  field_of_view_step = NW * H
  lower_r = lower_index * field_of_view_step
  upper_r = upper_index * (field_of_view_step + 1)
  memory_map = image_dataset[lower_r:upper_r,:]

And to get from here the w-th colour plane of the i-th field of view, the code would be:

.. code-block:: python

  row_offset = i*NW + w
  colour_image = memory[row_offset:row_offset +NW,:]

If the mosaic is sparse we can pack the mosaic and use a bisection algorithm to perform a binary
search to get the corresponding linear index used for the storage.

.. figure:: figure-linear-dataset.pdf
   :scale: 50%
   :figclass: bht

   A linear dataset for an acquisition having 3 colours where the pointer to a tile and a plane are
   shown. :label:`linear-dataset`

Remote Virtual Slide
====================

.. We have now defined a way to store our virtual slide and an API based on top of the stack
   HDF5-h5py.

We have now defined a framework to store our virtual slide based on top of the stack HDF5/h5py, that
relies on an HDF5 file stored on a local system or a network file system to work in a client-server
manner. This framework works perfectly, but a network file system has some limitations in comparison
to a real client-server framework. In particular a network file system is complex and has side
effects on an IT infrastructure, for example the need to setup an authentication mechanism for
security. Moreover we cannot build a complex network topology and route data on it.

We will now introduce the concept of remote virtual slide so as to add a real client-server feature
to our framework. We have two types of data to send over the network, the slide header and the
images. Since images are a flow of bytes, it is easy to send them over the network and use the Blosc
[Blosc]_ real-time compression to reduce the playload. For the slide header, we could serialise the
set of attributes to a JSON string, since the attributes data types are numbers, strings and tuples
of them.

.. seen as a male and female socket

For the networking layer, we use the ZeroMQ [ZMQ]_ library and its Python binding PyZMQ
[PyZMQ]_. ZeroMQ is a socket library that acts as a concurrency framework, carries message across
several types of socket and provide several connection patterns. This library is notably used by the
IPython framework for networking. The remote virtual slide framework use the request-reply pattern
to provide a client-server model. This pattern could be used to build a complex network topology
with data dealer, router and consumer. ZeroMQ is also an elegant solution to the global interpreter
lock [GIL]_ of the CPython interpreter that prevent real multi-threading. Indeed the connection
patterns and the message queues offer a simple way to exchange data between processes and
synchronise them.

Microscope Interconnection
--------------------------

As a first illustration of the remote virtual slide, we will look at the data flow between the
automatised microscope so called scanner and the software component, so called slide writer, that
write the HDF5 file on the file server. This client-server or producer-consumer framework is shown
on Figure :ref:`slide-writer-architecture`. To understand the design of this framework, we have to consider
these constrains. The first is due to the fact that the producer doesn't run at the same speed than
the consumer. Indeed we want to maximise the scanner throughput and at the same time maximise the
data compression which is a time consuming task. Thus there is a contradiction in our
requirements. Moreover the GIL prevent real time multi-threading. Thus we have to add a FIFO buffer
between the producer and the consumer so as to handle the speed difference between them. This FIFO
is called *slide proxy* and act as an image cache. The second constrain is due to the fact that the
slide writer could complete its job after the end of scan. It means the slide writer will not be
ready to process immediately another slide, which is a drawback if we want to scan a batch of
slide. Thus we need a third process called *slide manager* whose aim is to fork a slide writer for
each scan that will itself fork the slide proxy. Due to the fork mechanism, the three processes,
slide manager, slide writer and slide proxy must run on same host so called *slide server*. For the
other component, all the configuration could be envisaged.

The last component of this framework is the slide database whose aim is to store the path of the
HDF5 file on the slide server so as to retrieve easily the virtual slide.

.. Notes 
   slide header
   sequence diagram
   NFS

.. figure:: figure-scanner.pdf
   :scale: 50%
   :figclass: bht

   Virtual Slide Writer Architecture. :label:`slide-writer-architecture`

Image Viewer Graphic Engine
---------------------------

.. Notes 
   RTree free mosaic
   LRU cache
   SSD cache
   OpenGL -1,1
   8 and 10-bit monitor resolution dicom
   colour mixer matrix, colour status matrix, contrast matrix
   accuracy ? position rendering interpolation
   zoom manager, zoom layer 16 bin
   zoom > 1
   detection layer

.. figure:: figure-viewer.pdf
   :scale: 50%
   :figclass: bht

   Viewer Architecture. :label:`viewer-architecture`

The image viewer graphic engine works as Google Map using image tiles and follows our concept to
reconstruct the slide image online. We can imagine several strategies to reconstruct the slide
image. The first one would be to perform all the computation on CPU. But nowadays we have GPU that
offers an higher level of parallelism for such a task. GPU could be accessed using several API like
CUDA, OpenCL and OpenGL. The first ones are more suited for an exact computation and the last one
for image rendering. OpenGL API provides a way to perform a mapping of a 2D texture to a triangle
and by extension to a quad which is a particular form of a triangle strip. This feature is perfectly
suited to render a tile patchwork. Indeed the slide viewer requires to manage the viewport, the zoom
and an image processing to adjust the contrast for example. All these needs are provided by
OpenGL. Graphics items outside the viewport are discarded. Zoom is managed by texture sampler. And
fragment shaders provide a way to perform an image processing.

A texture could have from one to four colour component (RGBA), which make easy to render a slide
acquisition with up to four colours. To render more colours, we just need more than one texture by
tile and a more complicated fragment shader. If the tile are stored in planar format then we have to
convert them to an interleaved format, we call this task texture preparation. However we can also
use a texture per colour but in this case we have to take care to the maximal number of texture slot
provided by the OpenGL implementation, else we have to perform a blending. The main advantage of
using a multi-colour texture is for efficiency the since colour processing is vectorised
naturally. However if we want to register the colour online, then the texture lookup is anymore
efficient.

To render the viewport, the slide viewer must perform several tasks. First it must find the list of
tiles that compose the viewport and load these tiles from the HDF5 file. Then it must prepare the
data for the corresponding textures and load them to OpenGL. The time consuming task are last
three. In order to accelerate the rendering, it would be judicious to perform these tasks in
parallel, which is not simple using Python. For the loading, we could build on our remote virtual
slide to perform an intelligent read-ahead and to eventually prepare the data for the texture.  The
parallelisation of the texture loading is the most tricky and depends of the OpenGL implementation.
Modern XWindows server supports texture loading within a thread, but this approach couldn't be used
efficiently in Python due to the GIL. Moreover we can't use a process to do that since it requires
that process could share OpenGL context. Also we don't have guaranty the multi-threading would be
efficient in our case due to the fact we are rendering a patchwork and thus textures are short life
time. And the added complexity could be at the end a drawback.

Since our mosaic could be irregular, we cannot found by simple computation which tiles are in the
viewport. Instead we use an R-Tree for this purpose, that is an extension of B-Tree to 2D.

.. figure:: figure-viewport.pdf
   :scale: 50%
   :figclass: bht

   OpenGL viewport and texture painting. The overlapped black rectangles represent the mosaic of
   tiles. The red rectangle shows the viewport area. And the blue rectangle illustrates the
   rendering of a texture for a tile which is partially out of the viewport area. The horizontal
   line represents the sampling of the triangle using a scanline algorithm. Pixels out of the
   viewport are discarded. :label:`linear-dataset`

We use a subset OpenGL V4.x since the new programmable rendering pipeline improve considerably the
power of OpenGL. In modern OpenGL all the computations must be performed by hand from the viewport
modelling to the fragment processing, excepted the texture lookup which is supported by GSL
functions.

Since we are doing 2D rendering, it simplifies considerably the viewport model and the coordinate
transformation. OpenGL discards all the fragment that are outside the :math:`[-1,1]\times[-1,1]` 2D
interval. Thus to manage the viewport, we have to transform the slide frame coordinate using the
following model matrix:

.. math::
   :label: viewport matrix

   \left(\begin{array}{c}
   x \\
   y \\
   z \\
   w \\
   \end{array}\right)
   =
   \left(\begin{array}{cccc}
   \frac{2}{x_{sup} - x_{inf}} & 0 & 0 & -\frac{x_{inf} + x_{sup}}{x_{sup} - x_{inf}} \\
   0 & \frac{2}{y_{sup} - y_{inf}} & 0 & -\frac{y_{inf} + y_{sup}}{y_{sup} - y_{inf}} \\
   0 & 0 & 1 & 0 \\
   0 & 0 & 0 & 1 \\
   \end{array}\right)
   \left(\begin{array}{c}
   x_s \\
   y_s \\
   0 \\
   1 \\
   \end{array}\right)

where :math:`[x_{inf},x_{sup}]\times[y_{inf},y_{sup}]` is the viewport interval and
:math:`(x_s,y_s)` is a coordinate in the slide frame.

.. math::
   :label: normalised luminance

   % _\text{normalised
   \hat{l} = \frac{l - I_{inf}}{I_{sup} - I_{inf}}

.. math::
   :label: texture fragment shader

   \left(\begin{array}{c}
   r \\
   g \\
   b \\
   \end{array}\right)
   =
   \underbrace{
   \left(\begin{array}{ccc}
   m_{r0} & \ldots & m_{r3} \\
   m_{g0} & \ldots & m_{g3} \\
   m_{b0} & \ldots & m_{b3} \\
   \end{array}\right)
   }_\text{mixer matrix}
   \underbrace{
   \left(\begin{array}{ccc}
   s_0 & & \\
   & \ddots & \\
   & & s_3 \\
   \end{array}\right)
   }_\text{status matrix}
   \left(\begin{array}{c}
   \hat{l}_0 \\
   \vdots \\
   \hat{l}_3 \\
   \end{array}\right)

.. -------------------------------------------------------------------------------------------------

.. Customised LaTeX packages
.. -------------------------

.. Please avoid using this feature, unless agreed upon with the
.. proceedings editors.

.. ::

..   .. latex::
..      :usepackage: somepackage

..      Some custom LaTeX source here.

.. -------------------------------------------------------------------------------------------------

References
----------
.. [BigTIFF] Ole Eichhorn of Aperio, http://bigtiff.org
.. [Blosc] Francesc Alted, http://blosc.org, https://github.com/FrancescAlted/python-blosc
.. [GIL] http://www.dabeaz.com/python/UnderstandingGIL.pdf
.. [HDF5] HDF Group, http://www.hdfgroup.org/HDF5
.. [h5py] Andrew Collette and contributers, http://www.h5py.org
.. [IPython] http://ipython.org
.. [JSON] http://www.json.org
.. [LZF] Andrew Collette http://www.h5py.org/lzf, Marc Lehmann http://oldhome.schmorp.de/marc/liblzf.html
.. [Numpy] Travis Oliphant and Numpy developers, http://www.numpy.org
.. [OpenGL] Khronos Group, http://www.opengl.org
.. [PyOpenGL] http://pyopengl.sourceforge.net
.. [PyZMQ] https://github.com/zeromq/pyzmq
.. [ZMQ] iMatix Corporation, http://zeromq.org

.. -------------------------------------------------------------------------------------------------
   End
