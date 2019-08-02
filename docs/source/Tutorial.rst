.. _Tutorial:

Tutorial
=================================================

This page contains a basic runthrough of existing python code used to assist in the manual rate refresh from 2019.





First off, some dependencies must be imported for the code to run without errors.

.. code-block:: python

       >>> import sys
       >>> import pandas as pd

In order to utilize the package ``ActuarialOptimization``, the filepath containing the package must be added to Python's current
list of paths in which it looks for packages.

.. code-block:: python

       >>> sys.path.append(r'C:\...\scripts\ActuarialOptimization')
       >>> import ManualOptimization as mo

Now,  `Pandas <https://pandas.pydata.org/>`_ is used to read the data in from an excel file, and save it as a ``DataFrame`` under the the ``mydata`` variable name.

.. code-block:: python

       >>> mydata = pd.read_excel("myData.xlsx", sheet_name= "Current Factors")

The code is cleaned of all missing data entries (can also replace with median etc.). Also, the data is subset on years 2014+, 
and only those that are not hybrid policies. The shape of the DataFrame is printed to look at the changes made.

.. code-block:: python
       :emphasize-lines: 3,6,11

       >>> mydata=mydata.dropna(subset=["Manual_Expected_weighted"])
       >>> print(mydata.shape)
       (2354, 79)
       >>> mydata=mydata.dropna(subset=["SIC_Group_LDI"])
       >>> print(mydata.shape)
       (2354, 79)
       >>> mydata = mydata.loc[mydata["Hybrid_Indicator"] == 0]
       >>> mydata = mydata.loc[mydata["Year"] >= 2014]
       >>> mydata = mydata.reset_index()
       >>> print(mydata.shape)
       (2170, 80)

The :class:`~ManualOptimizationAE.Data` class is created. Note the second argument is a list containing column names of all of the factors that are being analyzed.
The third and fourth arguments are the column names for the Incurred Claim Amounts (weighted), and the current Manual Expected Claim Amounts (weighted).
Column Names can vary, so ensure they are entered correctly for the dataset being used.

It's at this point where the optional argument ``inOrder`` can be specified. If the Data class is passed ``inOrder = True`` (default), it will optimize the variables in the order they are given in the list. If ``inOrder = False``, then all variables are optimized simultaneously (this takes longer to run but can yield better results). This also comes with the optional parameter ``grouped`` (default False), where if set to ``True``, will group the variables by segments (summing up their ``actual`` and ``expected`` into one single number (similar to what would be seen in a pivot table). This leads to double counting, but can provide more accurate changes. 

.. code-block:: python

       >>> dataClass = mo.Data(mydata, ["SIC_Group_LDI", "Male_Pct", "SG_RR", "STD_Indicator", "SG_Max_Ben", "SG_Blue_Pct",
                "SG_CaseSize", "SG_Avg_Salary", "SG_Ben_Pct", "SG_Elim", "SG_OwnOcc", "SG_Partic"], actual = "Incurred_Claim_Amount_weighted",
                    expected = "Manual_Expected_weighted")

The :class:`Options` class is created. It is passed dataClass, the instance of ``Data``, and all other arguments are left default.
(See :class:`Options` for more information) 

.. code-block:: python

       >>> myOptions = mo.Options(dataClass)

Next, an instance of :class:`Optimize` is created, passing it myOptions (the instance of ``Options``), along with a boolean
indicator noting that there should be a credibility weight applied to each segment. Since this argument is set to ``True``, ``lifeYears``
must be given the column name that represents the total lifeYears in a policy.



**Note:** If set to False (default), each factor level can change withing 20% of its original (may lead to overcompensation
due to small sample sizes). If True, the lifeYears argument will be used to create a lower bound (the maximum of 0.9 and whatever the credibility says the bound can be), and an upper bound (the minimum of 1.1 and whatever the credibility says the bound can be).

.. code-block:: python

       >>> myOptimize = mo.Optimize(myOptions, credibility = True, lifeYears = "Life_Years")


Finally, the `differential_evolution <https://docs.scipy.org/doc/scipy/reference/generated/scipy.optimize.differential_evolution.html#scipy.optimize.differential_evolution>`_
can run. Note that it needs to be saved under three variables. The first variable represents the dictionary being returned containing
all of the variables, their level of factors, and optimized values. The second variable is the AE (Actual/Expected) ratio that would
be achieved if these factors had been in place. Lastly, the third variable is the sum of all absolute deviations of incurred to expected
at the end of the optimization (This is what is being minimized).

**Note:** There is a lot of excluded output from myOptimize.run() that is printed in the console. It has been excluded for increased
readability in this tutorial, yet may be useful in context. **This part of the code can run for a while, depending on the number of factors being optimized**.

.. code-block:: python
       :emphasize-lines: 3,5,7

       >>> final_dictionary, ending_AE, ending_abs_dev = myOptimize.run()
       >>> print(final_dictionary)
       {'SIC_Group_LDI': {'48:  Retail - Apparel & Accessories': 1.0, ..., '07: 75-79%': 0.9533748114180909, '05: 85-89%': 0.9757853818251141}}
       >>> print(ending_AE)
       0.8457173051580926
       >>> print(ending_abs_dev)
       88311962.01598422

