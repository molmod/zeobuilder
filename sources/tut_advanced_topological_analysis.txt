Topological analysis
####################

In the sections below, several zeolite models can be used:
:download:`sod_cage.zml <examples/sod_cage.zml>`, :download:`precursor.zml
<examples/precursor.zml>` and :download:`silicalite1.zml
<examples/silicalite1.zml>`.


T-atom coordination
===================

The fraction of Q1, Q2, Q3 and Q4 T-atoms is conventional measure for the
crystalinity of silica. In Zeobuilder, this information is obtained in two
steps:

1. Open one of the example models and select the global reference frame.

2. Activate the menu function ``Object -> Molecular -> T-atom coordination``. A
   popup dialog will appear, similar to this figure:

.. figure:: images/dialog_t_atom_coordination.png
    :align: center

    The t-atom coordination dialog

The ``Select`` buttons close the dialog and selects all the corresponding Qx
atoms.


Strong rings
============

In addition to the previous analysis, the enumeration of the strong rings is an
common method to clasify a zeolite model. For more information about rings in
crystal topologies, read the book
`Crystal Structures <http://www.public.asu.edu/~rosebudx/book.htm>`_ by
`M. O'Keeffe <http://www.public.asu.edu/~rosebudx/okeeffe.htm>`_ and B. G. Hyde,
in particular chapter 7. A few essential concepts are defined below:

Vertex
    A node in a graph. Vertices are connected by edges. In molecular topologies,
    vertices are atoms.

Edge
    A link in a graph. Edges connect vertices. In molecular topologies, edges
    are bonds.

Path
    A consecutive series of edges. A path connects two end vertices, via one or
    more consecutive edges.

Cycle
    A path where the end vertices coincide. It starts where it begins.

Ring
    A cycle for which no short cuts exist in the topology. Note that the
    definition of a ring also uses vertices and edges that are not part of the
    ring itself.

Strong ring
    A ring that can not be decomposed in smaller rings.

The enumeration of strong rings in Zeobuilder, takes the following steps:

1. Open one of the example models and select the global reference frame.

2. Activate the menu function ``Object -> Molecular -> Strong ring
   distribution``.

The results are presented in a window as shown in the figure below. The first tab
contains a histogram of the strong ring distribution, while the second tab
explicitly lists all strong rings. When selecting a strong ring from this list,
the corresponding atoms are selected (and hence highlighted in the 3D view).

.. figure:: images/strong_ring_distribution.png
    :align: center

    The strong ring distribution of the MFI precursor

We must give a few remarks here:

* The ring distribution code does not take into acount the periodicity of the
  system. For example, when the strong ring distribution is applied to the MFI
  structure, the analysis will list certain cycles that are clearly not strong
  rings.

* In the context of zeolites, a ring that contains 10 atoms, is actually a
  5T-ring. This annoyance can be circumvented, as shown in the following figure.
  Try to reproduce this.

.. figure:: images/strong_ring_distribution_si.png
    :align: center

    The strong ring distribution of the MFI precursor, without oxygen atoms.

