Installation
============

.. _Anaconda: https://www.anaconda.com/distribution/
.. _pyinstaller: https://pypi.org/project/PyInstaller/
.. _git: https://git-scm.com

Download binaries
-----------------
Once the project reaches its first release, downloadable (no installation needed) binaries for Windows, Mac OS X, and
Linux will become available. For the moment please follow the installation from source code instructions.

From source code
----------------
These instructions have been tested for Anaconda_ python. You can use any python distribution you like at risk of more
complications.

1. Clone the source code from https://github.com/glebdovzhenko/P61Viewer . You can install git_ for free and keep the
  project up to date, or just download the source code form github and unpack the archive.

.. code-block:: bash

    anyfolder $ git clone https://github.com/glebdovzhenko/P61Viewer.git

2. Set up a virtual environment (python version should be 3.5 since pyinstaller_ does not support newer versions yet)

.. code-block:: bash

    anyfolder $ conda create -n P61Venv python=3.5
    anyfolder $ conda activate

3. Change the directory to the project root

.. code-block:: bash

    anyfolder $ cd P61Viewer

4. Update pip and install the dependencies

.. code-block:: bash

    P61Viewer $ pip install pip --upgrade
    P61Viewer $ pip install -r requirements/base.txt

4.a If you are using Mac OS X, install the framework version of python and make sure (step 5.a) that it is the
interpreter you will be using to launch the application. It is necessary for most GUI python applications on Mac

.. code-block:: bash

    P61Viewer $ conda install -c anaconda python.app

5. (Windows, Linux) Change the directory to src and launch the application

.. code-block:: bash

    P61Viewer $ cd src
    src $ python P61ViewerMain.py

5.a (Mac OS X) Change the directory to src and launch the application

.. code-block:: bash

    P61Viewer $ cd src
    src $ pythonw P61ViewerMain.py