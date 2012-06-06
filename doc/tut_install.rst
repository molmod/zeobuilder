Installation
############

This tutorial explains step by step how to install Zeobuilder on your computer.


Preparing your mind
===================

Zeobuilder is developed and tested in modern Linux environments. The
installation instructions below are given for a Linux system only. If you want
to use Zeobuilder on other operating systems such as Windows or OSX, you should
have a minimal computer geek status to get it working. We are always interested
in hearing from your installation adventures.


Preparing your Linux system
===========================

Some software packages should be installed before Zeobuilder can be installed or
used. It is recommended to use the software package management of your Linux
distribution to install these dependencies.

The following software must be installed:

* Python 2.5, 2.6 or 2.7 (including the development files): http://www.python.org/
* Numpy >= 1.0: http://numpy.scipy.org/
* PyGTK >= 2.8: http://www.pygtk.org/
* PyOpenGL >= 2.0: http://pyopengl.sourceforge.net/
* PyGTKGLExt >= 1.1.0: http://www.k-3d.org/gtkglext/Main_Page
* librsvg2 >= 2.0: http://librsvg.sourceforge.net/
* libglade2 >= 2.0: http://www.jamesh.id.au/software/libglade/
* MatPlotLib >= 1.0: http://matplotlib.sourceforge.net/

Most Linux distributions can install this software with just a single terminal
command.

* Ubuntu 12.4::

    sudo apt-get install python-gtk python-opengl python-numpy python-gtkglext1 python-matplotlib python-numpy

* Fedora 17::

    sudo yum install {TODO}


MolMod dependency
=================


MolMod is a Python library used by most Python programs developed at the CMM.
Installation instructions can be found in the molmod documentation: TODO


Download the Zeobuilder source code
===================================

The source of the latest Zeobuilder version can be downloaded here:
https://github.com/molmod/zeobuilder/zipball/master


Actual installation
===================

If you have a previous installation of Zeobuilder, it is recommended to remove
it first::

    rm -v $HOME/bin/zeobuilder
    rm -vr $HOME/share/zeobuilder
    rm -vr $HOME/lib/python/zeobuilder

Change to the directory where the source code was downloaded. Then enter the
following commands::

    unzip molmod-zeobuilder-*.zip
    rm molmod-zeobuilder-*.zip
    cd molmod-zeobuilder-*
    ./setup.py install --home=~

