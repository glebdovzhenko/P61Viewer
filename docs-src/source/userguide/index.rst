User guide (updated for version 0.0.2)
======================================

Test files
----------

You can get the test files if you pull or download the repository. The files are in the
:code:`P61Viewer/test_files/generated` folder.

Open and view .nxs spectra
--------------------------

In P61 Viewer you can view and compare multiple :code:`.nxs` files at once. To do that click the "+" button:

.. image:: img/01-open.jpg

Once the files are open, you can show or hide their data from the plot by clicking the checkboxes next to their names.
To change visibility of multiple files at once, select them on the list and click the checkbox above.

.. image:: img/02-status.jpg

To close the files, select them on the list and click the "-" button.

.. image:: img/03-close.jpg

Note, that each :code:`.nxs` file contains two datasets coming from channels (detectors) 0 and 1.
Also note, that if you try to open a dataset that is already open, the program will do nothing.

Plot controls
-------------

Plot controls are standard for `matplotlib <https://matplotlib.org>`_ library. To autoscale, move, or magnify the plot you
have to first click the appropriate buttons below:

.. image:: img/04-mpl.jpg

Sequential fit with an arbitrary model
--------------------------------------

First make sure that all of the datasets you would like to fit are "checked" and visible on the plot.
Then you need to switch to the "Fit" tab by clicking it:

.. image:: img/05-fit.jpg

Now you need to select the fit area by scaling the plot (only data from the plot x scale will be taken for the fit).
In this case we focus on the two peaks in the middle of the spectrum