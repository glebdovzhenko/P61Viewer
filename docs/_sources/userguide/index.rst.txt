User guide (updated for version 0.0.2)
======================================

Test files
----------

You can get the test files if you clone or download the `repository <https://github.com/glebdovzhenko/P61Viewer>`_.
The files are in the :code:`P61Viewer/test_files/generated` folder.

Open and view .nxs spectra
--------------------------

In P61 Viewer you can view and compare multiple :code:`.nxs` files at once. To do that click the "+" button:

.. image:: 01-open.jpg

Once the files are open, you can show or hide their data from the plot by clicking the checkboxes next to their names.
To change visibility of multiple files at once, select them on the list and click the checkbox above.

.. image:: 02-status.jpg

To close the files, select them on the list and click the "-" button.

.. image:: 03-close.jpg

Note, that each :code:`.nxs` file contains two datasets coming from channels (detectors) 0 and 1.
Also note, that if you try to open a dataset that is already open, the program will do nothing.

Plot controls
-------------

Plot controls are standard for `matplotlib <https://matplotlib.org>`_ library. To autoscale, move, or magnify the plot you
have to first click the appropriate buttons below:

.. image:: 04-mpl.jpg

Sequential fit with an arbitrary model
--------------------------------------

Preparation
~~~~~~~~~~~

First make sure that all of the datasets you would like to fit have checked boxes next to them.
Then you need to switch to the "Fit" tab by clicking it:

.. image:: 05-fit.jpg

Now you need to select the fit area by scaling the plot, since only data within the plot x range will be taken for the fit.
In this case we want to focus on the two peaks in the middle of the spectrum.

.. image:: 06-area.jpg

Model builder
~~~~~~~~~~~~~

Now let us have a look at the interface. First we have the fit model builder:

.. image:: 07-builder.jpg

On the left side of the model builder you have the list of all available models, and on the right the models,
sum of which will be used for the fit.
To add a model to the list on the right, select it in the left list and click the right-pointing arrow button.
To remove a model from the list on the right, select it in the right list and click the left-pointing arrow button.

For this dataset we are going to use two pseudo-Voigt functions and a linear function. After adding them to the model
the result should look like this:

.. image:: 08-composite.jpg

Note that on the right list all models have a shortened unique name after a colon: :code:`PseudoVoigtModel:pv0`,
:code:`PseudoVoigtModel:pv1`, :code:`LinearModel:lin0`. This short name is used as a prefix in model parameter names,
so that all parameter names in the fit are unique.
For instance, parameter name :code:`pv0_amplitude` is the amplitude of the pseudo-Voigt model :code:`pv0`.
A description of all models, their parameters and their meaning can be found
`here <https://lmfit.github.io/lmfit-py/builtin_models.html>`_.

Model inspector
~~~~~~~~~~~~~~~

Now that we have defined our model, let us look at the model inspector:

.. image:: 09-inspector.jpg

It shows the parameter values, errors and limits specific to the selected dataset. The first column, "Fit", marks if
the parameter will be varied during the next optimization. Columns "Name", "Value", and "STD" are self-explanatory,
amd the columns "Min" and "Max" (scroll the table right to see them) show the limits within which the parameters will
be varied. Columns "Value", "Min", and "Max" are editable by double-clicking the cells and accept floating point
numbes in any format, including :code:`INF` and :code:`-INF` for the limits. So the next step is to edit the parameter
values until you have a reasonable starting point for the fit. If you like, you can edit the limits too.
The result may look like this:

.. image:: 10-params.jpg

And now you are ready for the first fit. Click "Fit this" button, and if everything goes right, the result will look
like this:

.. image:: 11-fit-this.jpg

Sequential fit
~~~~~~~~~~~~~~


Export
~~~~~~

