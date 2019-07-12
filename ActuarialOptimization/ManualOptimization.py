
#Paul Frydryk
#2019
#The purpose of this file is to attempt to ease the process of undergoing
#a manual rate refresh. Instead of having to rewrite code to adapt to
#minor changes, this file will act as a template (and possibly a guideline).


import numpy as np
import pandas as pd
import time
import scipy
from scipy import optimize
import warnings
warnings.filterwarnings("error")

class Data:

    """
    Data class used in optimization.

    :param df: The `pandas` dataframe containing final filtered data. Note: Data should already be scrubbed, containing NaNs can cause problems further down the line.
        best practice is to already subset data on preliminary conditions.
    :param variables: A list of all variable names as shown in their respective columns.
    :param actual: A string containing the column name of Incurred Claim Costs (Weighted?)
    :param expected: A string containing the column name of the Manual Expected Claim Costs (Weighted?)

    :type df: `Pandas DataFrame <https://pandas.pydata.org/pandas-docs/stable/reference/api/pandas.DataFrame.html>`_
    :type variables: list
    :type actual: str
    :type expected: str

    :ivar df: The Pandas dataframe containing underlying data
    :ivar vars: Variables being optimized
    :ivar actual: The name of the Actual Incurred Claims column in df
    :ivar expected: The name of the Manual Expected Claims column in df
    :ivar levels: The dictionary containing all factor levels for all variables passed from `variables`




    """
    def __init__(self, df, variables, actual, expected):
        self.df = df
        self.vars = variables
        self.actual = actual
        self.expected = expected
        self.__getLevels()
        self._initialAE = df[actual].sum()/df[expected].sum()
    def __getLevels(self):
        self.levels = {}
        #Putting factor levels into the dictionary
        for v in self.vars:
            self.levels[v]=self.df[v].unique()
class Options:
    """
    Class containing specifications about optimization technique. Most of the arguments can be left as defaults.
    These arguments are transferred to the `SciPy` optimization technique `differential_evolution <https://docs.scipy.org/doc/scipy/reference/generated/scipy.optimize.differential_evolution.html#scipy.optimize.differential_evolution>`_

    :param data: An object of the type :class:`Data`
    :param strategy: The differential evolution strategy to use.
     Should be one of:

        * ‘best1bin’
        * ‘best1exp’
        * ‘rand1exp’
        * ‘randtobest1exp’
        * ‘currenttobest1exp’
        * ‘best2exp’
        * ‘rand2exp’
        * ‘randtobest1bin’
        * ‘currenttobest1bin’
        * ‘best2bin’
        * ‘rand2bin’
        * ‘rand1bin’

        The default is ‘best1bin’.
    :param maxiter: The maximum number of generations over which the entire population is evolved. The maximum number of function evaluations (with no polishing) is: ``(maxiter + 1) * popsize * len(x)``
    :param popsize: A multiplier for setting the total population size. The population has ``popsize * len(x)`` individuals (unless the initial population is supplied via the init keyword).
    :param tol:  Relative tolerance for convergence, the solving stops when ``np.std(pop) <= atol + tol * np.abs(np.mean(population_energies))``, where and atol and tol are the absolute and relative tolerance respectively.
    :param mutation: The mutation constant. In the literature this is also known as differential weight, being denoted by F. If specified as a float it should be in the range ``[0, 2]``. If specified as a tuple ``(min, max)`` dithering is employed. Dithering randomly changes the mutation constant on a generation by generation basis. The mutation constant for that generation is taken from ``U[min, max)``. Dithering can help speed convergence significantly. Increasing the mutation constant increases the search radius, but will slow down convergence.
    :param recombination: The recombination constant, should be in the range ``[0, 1]``. In the literature this is also known as the crossover probability, being denoted by CR. Increasing this value allows a larger number of mutants to progress into the next generation, but at the risk of population stability.
    :param seed: If seed is not specified the np.RandomState singleton is used. If seed is an int, a new np.random.RandomState instance is used, seeded with seed. If seed is already a np.random.RandomState instance, then that np.random.RandomState instance is used. Specify seed for repeatable minimizations.
    :param disp: Display status messages
    :param callback: A function to follow the progress of the minimization. ``xk`` is the current value of ``x0``. val represents the fractional value of the population convergence. When ``val`` is greater than one the function halts. If callback returns `True`, then the minimization is halted (any polishing is still carried out).
    :param polish: If True (default), then `scipy.optimize.minimize <https://docs.scipy.org/doc/scipy/reference/generated/scipy.optimize.minimize.html#scipy.optimize.minimize>`_ with the L-BFGS-B method is used to polish the best population member at the end, which can improve the minimization slightly.
    :param init: Specify which type of population initialization is performed. Should be one of:

        * ‘latinhypercube’
        * ‘random’
        * array specifying the initial population. The array should have shape (M, len(x)), where len(x) is the number of parameters. init is clipped to bounds before use.

        The default is ‘latinhypercube’. Latin Hypercube sampling tries to maximize coverage of the available parameter space. ‘random’ initializes the population randomly - this has the drawback that clustering can occur, preventing the whole of parameter space being covered. Use of an array to specify a population subset could be used, for example, to create a tight bunch of initial guesses in an location where the solution is known to exist, thereby reducing time for convergence.
    :param atol: Absolute tolerance for convergence, the solving stops when ``np.std(pop) <= atol + tol * np.abs(np.mean(population_energies))``, where and atol and tol are the absolute and relative tolerance respectively.
    :param updating: If 'immediate', the best solution vector is continuously updated within a single generation [4]. This can lead to faster convergence as trial vectors can take advantage of continuous improvements in the best solution. With 'deferred', the best solution vector is updated once per generation. Only 'deferred' is compatible with parallelization, and the workers keyword can over-ride this option

        **Note: Seems to not converge in finite time? I wouldn't utilize this argument**

    :param workers: If workers is an int the population is subdivided into workers sections and evaluated in parallel (uses **multiprocessing.Pool**). Supply -1 to use all available CPU cores. Alternatively supply a map-like callable, such as multiprocessing.Pool.map for evaluating the population in parallel. This evaluation is carried out as workers ``(func, iterable)``. This option will override the updating keyword to ``updating='deferred'`` if ``workers != 1``. Requires that func be pickleable.

        **Note: See above note**


    :type data: :class:`Data`
    :type strategy: str, optional
    :type maxiter: int, optional
    :type popsize: int, optional
    :type tol: float, optional
    :type mutation: float or tuple(float, float), optional
    :type recombination: float, optional
    :type seed: int or np.random.RandomState, optional
    :type disp: bool, optional
    :type callback: callable, callback(xk, convergence=val), optional
    :type polish: bool, optional
    :type init: str or array-like, optional
    :type atol: float, optional
    :type updating: {'immediate','deferred'}, optional
    :type workers: int or map-like callable, optional
    """


    def __init__(self, data, strategy='best1bin', maxiter=1000, popsize=15, tol=0.01, mutation=(0.5, 1),
                 recombination=0.7, seed=None,  disp=False, callback=None, polish=True, init='latinhypercube', atol=0,
                 updating='immediate', workers=1):

        """
        Most options can be left as defaults, but `data` must be passed a Data class.
        """

        assert isinstance(data, Data), "Parameter 'data' must be an instance of the Data class."

        self.data = data
        self.strategy = strategy
        self.maxiter = maxiter
        self.popsize = popsize
        self.tol = tol
        self.mutation = mutation
        self.recombination = recombination
        self.seed = seed
        self.callback = callback
        self.disp = disp
        self.polish = polish
        self.init = init
        self.atol = atol
        self.updating = updating
        self.workers = workers



    def __abs_dev(self, factorlist, variable):
        """
        :param factorlist: The current set of factors for the given variable.
        :param variable: The variable currently being optimized.
        :return abs_dev: The resulting sum of absolute deviations of Actual vs Expected across all policies for the given factorlist.
        """
        global factor_dict
        factor_dict = {}
        for i in range(len(self.data.levels[variable])):
            factor_dict[self.data.levels[variable][i]] = factorlist[i]

        abs_dev = 0
        new_exp_weighted = 0

        for i in range(len(self.data.df[variable])):
            new_exp_weighted += self.data.df[self.data.expected][i] * factor_dict[self.data.df[variable][i]]

        new_AE = sum(self.data.df[self.data.actual]) / new_exp_weighted

        for i in range(len(self.data.df[variable])):
            abs_dev += abs(self.data.df[self.data.expected][i] * factor_dict[self.data.df[variable][i]] * new_AE -
                           self.data.df[self.data.actual][i])

        if new_AE < self.data._initialAE * 0.9 or new_AE > self.data._initialAE * 1.1:
            abs_dev += 1e10

        return abs_dev




class Optimize:
    """
    Class that runs the optimization based off of :class:`Data` and :class:`Options`.

    :param options: The options class created to pass to     These arguments are transferred to the `SciPy` optimization technique `differential_evolution <https://docs.scipy.org/doc/scipy/reference/generated/scipy.optimize.differential_evolution.html#scipy.optimize.differential_evolution>`_
    :param credibility: Whether or not to factor in credibility, based on Life Years in the segment. If set to True, `lifeYears` must also be given an argument.

        Default is ``False``
    :param lifeYears: The name of the column in the ``df`` which was passed to the :class:`Data` class which represents the Life Years per policy.

        Default is ``None``

    :type options: :class:`Options`
    :type credibility: bool, optional
    :type lifeYears: str, optional
    """

    def __init__(self, options, credibility = False, lifeYears = None):
        assert isinstance(options, Options), "Parameter 'options' must be an instance of the Options class."

        if lifeYears:
            if not credibility:
                print("Credibility set to False, but life years given an argument. Change this using the setCredibility() method.")
        if not lifeYears:
            if credibility:
                print("Credibility set to True, but lifeYears not given an argument. Change this by using the setLifeYears() method.")
        if not lifeYears and not credibility:
            print("Not using credibility will default all factors to change within a 20% range. You can decide to use credibility later by using the setCredibility() and setLifeYears() methods.")

        self.options = options
        self.credibility = credibility
        self.lifeYears = lifeYears
        self.bounds_lower = {}
        self.bounds_upper = {}
        self.__checkCredibility()


    def setCredibility(self, newCred):
        """
        :param newCred: Boolean of whether or not to use credibility.
        :type newCred: bool
        """
        self.credibility = newCred
        self.__checkCredibility()
    def setLifeYears(self, newLifeYears):
        """
        :param newLifeYears: String consisting of column name of LifeYears
        :type newLifeYears: str
        """
        self.lifeYears = newLifeYears
        self.__checkCredibility()
    def __checkCredibility(self):
        if self.credibility and self.lifeYears:
            try:
                self.options.data.df[self.lifeYears]
            except KeyError:
                raise KeyError(self.lifeYears+" is not a valid column name.")
            self.__createCredibility()
        else:
            self.bounds_lower = {}
            self.bounds_upper = {}
            for var in self.options.data.vars:
                self.bounds_lower[var]=[0.8]*len(self.options.data.levels[var])
                self.bounds_upper[var]=[1.2]*len(self.options.data.levels[var])



    def __createCredibility(self):
        self.bounds_lower = {}
        self.bounds_upper = {}
        for v in self.options.data.vars:
            lb = []
            ub = []
            x = 0
            for f in self.options.data.levels[v]:
                try:
                    credibility = np.sqrt(self.options.data.df.loc[self.options.data.df[v] == f, self.lifeYears].sum() / 400000)
                    AEratio = (self.options.data.df.loc[self.options.data.df[v] == f, self.options.data.actual].sum() / self.options.data.df.loc[
                        self.options.data.df[v] == f, self.options.data.expected].sum()) / (
                                          sum(self.options.data.df[self.options.data.actual]) / sum(
                                      self.options.data.df[self.options.data.expected]))
                    bound = AEratio * credibility + (1 - credibility)

                    if bound < 1:
                        ub.append(1)
                        lb.append(bound)
                    if bound >= 1:
                        ub.append(bound)
                        lb.append(1)
                    if np.isnan(bound):
                        ub.append(1)
                        lb.append(1)
                except(RuntimeWarning):
                    raise RuntimeWarning("Unexpected value in "+str(v)+". Hint: Check for nulls.")
            self.bounds_lower[v] = lb
            self.bounds_upper[v] = ub

    def __abs_dev(self, factorlist, variable):
        """

        :param factorlist: The current set of factors for the given variable.
        :param variable: The variable currently being optimized.
        :return abs_dev: The resulting sum of absolute deviations of Actual vs Expected across all policies for the given factorlist.
        """
        global factor_dict
        factor_dict = {}
        for i in range(len(self.options.data.levels[variable])):
            factor_dict[self.options.data.levels[variable][i]] = factorlist[i]

        new_exp_weighted = sum(
            self.options.data.df[self.options.data.expected] * self.options.data.df[variable].map(factor_dict))

        new_AE = sum(self.options.data.df[self.options.data.actual].values) / new_exp_weighted
        abs_dev = sum(abs(self.options.data.df[self.options.data.expected] * self.options.data.df[variable].map(factor_dict) *
                          new_AE - self.options.data.df[self.options.data.actual].values))

        if new_AE < self.options.data._initialAE * 0.9 or new_AE > self.options.data._initialAE * 1.1:
            abs_dev += 1e10
        return abs_dev


    def __change_manual_expected(self, factorlist, factor):


        factor_dict = {}

        for i in range(len(self.options.data.levels[factor])):
            factor_dict[self.options.data.levels[factor][i]] = factorlist[i]
        self.options.data.df[self.options.data.expected]=self.options.data.df[self.options.data.expected]\
                                                         * self.options.data.df[factor].map(factor_dict)



    def run(self):
        """
        Runs the `differential_evolution <https://docs.scipy.org/doc/scipy/reference/generated/scipy.optimize.differential_evolution.html#scipy.optimize.differential_evolution>`_
        minimizing the absolute deviation of Manual Expected to Incurred by setting sets of factors to be multiplied by the original Manual Expected.

        :return: Tuple of the a dictionary containing variables and their factors, along with minimized absolute deviation and AE.

        **Note: When using** ``Optimize.run()``, **it should be assigned as follows.**

        ``final_dictionary, endingAE, endingAbsDev = myOptimize.run()``
        """
        print("==========================================================")
        print("__________________________________________________________")
        print("|             Running Actuarial Optimization             |")
        print("̅̅̅̅̅̅̅̅̅̅̅̅̅̅̅̅̅̅̅̅̅̅̅̅̅̅̅̅̅̅̅̅̅̅̅̅̅̅̅̅̅̅̅̅̅̅̅̅̅̅̅̅̅̅̅̅̅̅")
        print("==========================================================")
        final_dict = {}
        start_dev = sum(abs(self.options.data.df[self.options.data.expected].values *
                            sum(self.options.data.df[self.options.data.actual].values) /
                            sum(self.options.data.df[self.options.data.expected].values)
                            - self.options.data.df[self.options.data.actual].values))
        print("Starting absolute deviation: ", start_dev)
        print("Starting AE", sum(self.options.data.df[self.options.data.actual])/sum(self.options.data.df[self.options.data.expected]))
        print("Starting optimization date and time: ", time.asctime( time.localtime(time.time()) ))
        print("__________________________________________________________")
        current = 1
        for f in self.options.data.vars:
            print("Currently working on "+f+", variable "+str(current)+"/"+str(len(self.options.data.vars))+".")
            print("Absolute Deviation before working on "+f+": "+ str(sum(abs(self.options.data.df[self.options.data.expected].values *
                            sum(self.options.data.df[self.options.data.actual].values) /
                            sum(self.options.data.df[self.options.data.expected].values)
                            - self.options.data.df[self.options.data.actual].values))))
            current += 1
            xmin = self.bounds_lower[f]
            xmax = self.bounds_upper[f]
            bounds = [(low, high) for low, high in zip(xmin, xmax)]
            res = scipy.optimize.differential_evolution(self.__abs_dev, bounds = bounds, args = (f,),
                                                        strategy = self.options.strategy, maxiter = self.options.maxiter,
                                                        popsize = self.options.popsize, tol = self.options.tol,
                                                        mutation = self.options.mutation, recombination = self.options.recombination,
                                                        seed = self.options.seed, callback = self.options.callback,
                                                        disp = self.options.disp, polish = self.options.polish,
                                                        init = self.options.init, atol = self.options.atol,
                                                        updating = self.options.updating, workers= self.options.workers)
            temp_dict = {}
            for k in range(len(self.options.data.levels[f])):
                temp_dict[self.options.data.levels[f][k]] = res.x[k]
            final_dict[f]=temp_dict.copy()
            self.__change_manual_expected(res.x, f)
            print("Absolute Deviation after working on "+f+": "+ str(res.fun))

            print("==========================================================")

        endingAE = sum(self.options.data.df[self.options.data.actual])/sum(self.options.data.df[self.options.data.expected])
        endingdev = res.fun

        print("Ending optimization date and time",time.asctime( time.localtime(time.time()) ))

        return final_dict, endingAE, endingdev


