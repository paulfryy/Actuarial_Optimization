.. ActuarialOptimizationMaster documentation master file, created by
   sphinx-quickstart on Thu Jul 11 09:01:27 2019.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to ActuarialOptimization's documentation!
=======================================================



The purpose of this package is to attempt to ease the process of undergoing a manual rate refresh. 
Instead of having to rewrite code to adapt to minor changes, this package will act as a template (and possibly a guideline).

The requirements to be able to use this package are as follows:

* Must be interested in minimizing the sum of all absolute deviations of Incurred Claim amounts against Manual Expected Claim amounts. 
	* That is,  minimizing :math:`\sum{\text{abs(Incurred - Expected)}}`

* A datafile must be obtained that has individual columns representing variables that are being changed in the manual.
	* On top of this, these columns must contain values representing levels on which the factor is applied (For instance,the same levels which the manual applies).

* The datafile must have incurred claim costs, as well as expected claim costs (weighted is preferable, but not required).
				  

**Note: The resulting factors are increases/decreases. For instance, a factor of 95% does NOT mean the manual should quote that segment at a 5% discount, rather the factor should be 95% of what it currently is.**



.. toctree::
   :maxdepth: 5
   :caption: Contents:

   Modules<modules>
   Full Tutorial<Tutorial>
   Download Source Files<https://github.com/paulfryy/Actuarial_Optimization>



Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
* :ref:`Tutorial/Walkthrough <Tutorial>`
* :ref:`How to import local modules <Modules>`


Utilized Packages
=================

* `SciPy <https://www.scipy.org/>`_
* `Pandas <https://pandas.pydata.org/>`_
* `NumPy <http://www.numpy.org/>`_
* `time <https://docs.python.org/3/library/time.html>`_
