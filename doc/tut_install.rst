Installation
############


Disclaimer
==========

Zeobuilder is developed and tested on modern Linux environments. The
installation instructions below are given for a Linux system only. If you want
to use Zeobuilder on other operating systems such as Windows or OSX, you should
have a minimal computer geek status to get it working. We are always interested
in hearing from your installation adventures.


MolMod dependency
=================

`MolMod <http://molmod.github.com/molmod/>`_ is a Python library used by most
Python programs developed at the CMM. It must be installed before Zeobuilder can
be used or installed. Installation and download instructions can be found in the
`molmod documentation <http://molmod.github.com/molmod/tutorial/install.html>`_.
The instructions below only work if the MolMod package is installed.


External dependencies
=====================

Some software packages should be installed before Zeobuilder can be installed or
used. It is recommended to use the software package management of your Linux
distribution to install these dependencies.

The following software must be installed:

* Python 2.5, 2.6 or 2.7: http://www.python.org/
* Numpy >= 1.0: http://numpy.scipy.org/
* PyGTK >= 2.8: http://www.pygtk.org/
* PyOpenGL >= 2.0: http://pyopengl.sourceforge.net/
* PyGTKGLExt >= 1.1.0: http://www.k-3d.org/gtkglext/Main_Page
* librsvg2 >= 2.0: http://librsvg.sourceforge.net/
* libglade2 >= 2.0: http://www.jamesh.id.au/software/libglade/
* MatPlotLib >= 1.0: http://matplotlib.sourceforge.net/

Most Linux distributions can install this software with just a single terminal
command.

* Ubuntu 14.4 and up::

    sudo apt-get install python-gtk2 python-opengl python-numpy python-gtkglext1 python-matplotlib python-rsvg

* Fedora 21 and up::

    sudo yum install pygtk2 pygtk2-libglade PyOpenGL numpy pygtkglext python-matplotlib gnome-python2-rsvg


Installing the latest version of Zeobuilder
===========================================

The following series of commands will download the latest version of Zeobuilder,
and will then install it into your home directory. ::

    cd ~/build/
    git clone git://github.com/molmod/zeobuilder.git
    (cd zeobuilder; ./setup.py install --user)

The option ``--user`` can be ommitted when you are installing into a conda
envirnoment or a pip virtual environment.

You are now ready to start using Zeobuilder!


Testing your installation
=========================

For the development and testing one needs to install additional packages

* Nosetests >= 0.11: http://somethingaboutorange.com/mrl/projects/nose/0.11.2/
* Sphinx >= 1.0: http://sphinx.pocoo.org/

Most Linux distributions can install this software with just a single terminal command:

* Ubuntu 12.4::

    sudo apt-get install python-nose python-sphinx

* Debian 5::

    su -
    apt-get install python-nose python-sphinx
    exit

* Fedora 17::

    sudo yum install python-nose sphinx

* Suse 11.2::

    sudo zypper install python-nose sphinx

Once these dependencies are installed, execute the following commands to run the
tests::

    cd ~/build/zeobuilder
    nosetests -v

If some tests fail, post the output of the tests on the `Zeobuilder
mailing list <https://groups.google.com/forum/#!forum/zeobuilder>`_.

