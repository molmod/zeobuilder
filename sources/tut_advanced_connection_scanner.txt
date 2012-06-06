The connection scanner
######################

Spring objects, as discussed in chapter A5, can be used to connect two or more
zeolite clusters (building blocks), but one has to select manually the pairs of
oxygen atoms that will join to form new Si-O-Si bridges. The Connection Scanner
also automates the search for such pairs of oxygen atoms, given two molecular
building blocks. In this chapter, we demonstrate the usage of the scanner on the
basis of the MFI precursor (:download:`precursor.zml <examples/precursor.zml>`).

One or two building blocks must be selected, before activating ``Object ->
Builder -> Connection Scanner``. A building block consists of a reference frame
that contains the molecular structure of the building block. (This can not be
the global reference frame. It must be a subframe.) When only one building
block is selected, the scanner will search for possible ways to connect that
building block and with an identical copy. After the menu function ``Object ->
Builder -> Connection Scanner`` is activated, a dialog pops up where one can
enter all the scanner parameters. This dialog contains three tabs: ``Geometry1``,
``Geometry2`` and ``Parameters``, which are shown in the figures below. The
first two tabs are identical. The second is only applicable when two building
blocks are selected. The third tab contains all the parameters that control the
behavior of the Connection Scanner algorithm.

.. figure:: images/conscan_dialog_tab1.png
    :align: center

    The first tab of the Connection Scanner dialog


.. figure:: images/conscan_dialog_tab3.png
    :align: center

    The third tab of the Connection Scanner dialog

.. note::

    It may be instructive to repeat the chapter discussing the springs,
    :doc:`tut_basic_springs`, where the condensation algorithm is explained in
    detail. The remainder of this chapter assumes that the reader is familiar
    with that concept.


Example 1: A triangle-based search
==================================

In this example, all possible connections between two zeolite building units
are generated, in which a triangle of oxygen atoms in one unit geometrically
overlaps with a matching triangle in a second building unit.

We will first explain the steps to apply the connection scanner. Later on, the
effect of the parameters and the end result is discussed.

1. Load the model :download:`precursor.zml <examples/precursor.zml>` and select
   the frame that contains the building block.

2. Activate the menu function ``Object -> Builder -> Connection Scanner`` and
   fill in the following parameters:

   * Tab ``Geometry 1``:

    * **Connecting points - Filter expression**: ``isinstance(node, Atom) and node.number == 8 and node.num_bonds() == 1``

    * **Connecting points - Radius expression**: ``node.get_radius()``

    * **Repulsive points - Filter expression**: ``isinstance(node, Atom) and (node.number == 8 or node.number == 14)``

    * **Repulsive points - Radius expression**: ``node.get_radius()*1.5``

   * Tab ``Geometry 2``: (disabled)

   * Tab ``Parameters``:

    * **Action radius**: ``8 A`` (A stands for angstrom)

    * **Distance tolerance**: ``0.15 A``

    * Select **Allow free rotations**

    * Check **Allow inversion rotations**

    * **Minimum triangle size**: ``0.15 A``

   Click `OK`

3. A progress dialog appears as in this figure:

   .. figure:: images/conscan_dialog_progress.png
       :align: center

       The progress dialog of the connection scanner.

4. When the Connection Scanner has finished, Click ``OK`` again.

5. A duplicate of the original building block is added to the model and an
   object ``ConscanResults`` is added to the folder. Double click on
   ``ConscanResults`` in the tree view. A tool window opens that lists all the
   results of the connection scanner, similar to the figure below. Select an
   item in the list, and the corresponding connection is displayed in the 3D
   view.

   .. figure:: images/conscan_results.png
       :align: center

       The results of the connection scanner.

6. In the results window, the button ``Apply and optimize`` will further
   optimize the relative orientation of the building blocks, using springs.

This should already give a nice impression of the capabilities of the Connection
Scanner. We will now discuss the signification of the parameters for the
connection scanner in detail:

* **Connecting points - Filter expression**: This python expression must be True
  when the variable `node` is one of the candidate atoms in the building block
  that should be brought into overlap with a similar atom in the other building
  block, in order to form a proper connection between the two blocks. In the
  case of Zeolites, where clusters join through a poly-condensation reaction,
  this expression must select the termination oxygen atoms.

* **Repulsive points - Filter expression**: This is a similar python expression,
  but it must be True for the atoms in the building block that are not allowed
  to overlap when two blocks are connected. In the case of zeolite clusters,
  this includes the Silicon atoms and the internal Oxygen atoms. Note that the
  expression for the repulsive points is only evaluated for atoms that are not
  selected with the filter expressions for the connecting points.

* **Allow free rotations** versus **Use a fixed rotation**: When free rotations
  are allowed, the connection scanner will search for matching connections, by
  enumerating and comparing all triangles formed by connecting points in the
  first and second building block. When two congruent triangles are found (one
  in the first block and the other one in the second block), a Galilean
  transformation must exist that, when applied to the second block, brings the
  the triangle in the first block into overlap with the triangle in the second
  block. When using a fixed rotation, the scanner search for pairs of connecting
  points in both blocks that have a matching relative position.

* **Action radius**: This parameter determines the maximum length of the
  triangle edges when searching for matching triangles, or it is the upper limit
  for the pair distance when searching for matching atom pairs.

* The **Distance tolerance** is the maximum allowed mismatch between two inter
  atomic distances when searching for matching triangles or atom pairs.

* The option **Allow inversion rotations**, will also consider mirrored copies
  of the building blocks.

* **Minimum triangle size**: This parameter is introduced to eliminate the
  (rare) situation where the triangle formed by three connecting points becomes
  degenerate. Internally this value is converted to a 'minimum triangle area'
  and it eliminates cases where tree connecting points are co-linear. Such
  triangles do not properly define a relative orientation for the two building
  blocks.

* **Connecting points - Radius expression** and **Repulsive points - Radius
  expression**: At a certain point, the Connection Scanner must determine the
  quality of each possible connection between two building blocks. The quality
  of a connection is determined by counting all pairs of overlapping connecting
  points. From that number, the amount of pairs of overlapping points that
  include at least one repulsive point, is subtracted. Overlapping pairs are
  counted on the basis of `Fuzzy logic
  <http://en.wikipedia.org/wiki/Fuzzy_logic>`_: For each atom pair a score is
  determined based on their inter-atomic distance and their radii. The sum of
  all these scores represents the quality of a connection. An overlapping pair
  results in a score of plus (or minus) one when the two atoms exactly coincide.
  The score is zero when the distance between the two atoms is larger than the
  sum of their radii. For the intermediate cases, the score is interpolated
  between plus (or minus) one and zero, based on the inter-atomic distance.


Example 2: A pair-based search
==============================

In this example, all possible connections between two zeolite building units
are generated, in which a pair of oxygen atoms in one unit geometrically
overlaps with a matching pair in a second building unit.

These are the straightforward instructions to perform this example:

1. Load the model :download:`precursor.zml <examples/precursor.zml>` and select
   the frame that contains the building block.

2. Activate the menu function ``Object -> Builder -> Connection Scanner`` and
   fill in the following parameters:

   * Tab ``Geometry 1``:

    * **Connecting points - Filter expression**: ``isinstance(node, Atom) and node.number == 8 and node.num_bonds() == 1``

    * **Connecting points - Radius expression**: ``node.get_radius()``

    * **Repulsive points - Filter expression**: ``isinstance(node, Atom) and (node.number == 8 or node.number == 14)``

    * **Repulsive points - Radius expression**: ``node.get_radius()*1.5``

   * Tab ``Geometry 2``: (disabled)

   * Tab ``Parameters``:

    * **Action radius**: ``8 A`` (A stands for angstrom)

    * **Distance tolerance**: ``0.15 A``

    * Select **Use a fixed rotation**

    * Enter the following rotation parameters: angle=180°, n=(0,1,0), inversion=False

   Click ``OK``

3. The remainder is similar to the previous section.



