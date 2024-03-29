
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
    :param variables: A list of all variable names as shown in their respective columns (for use in optimizing sequentially). This parameter also takes a dictionary if optimizing all variables at once is desired.
    :param actual: A string containing the column name of Incurred Claim Costs (Weighted?)
    :param expected: A string containing the column name of the Manual Expected Claim Costs (Weighted?)
    :param inOrder: A boolean containing the option to run the optimization sequentially (True), or all factors at once (False). Default is `True`.
    :param grouped: A boolean containing the option to group the data based off on the variables given. Instead of looking at the data at an individual sample level and finding aggregate absolute deviation, it will group the data by variable factor level, and find the absolute deviation within these groups (and sum them up). Default is False, and if inOrder = True, this must be set to False.
    :type df: `Pandas DataFrame <https://pandas.pydata.org/pandas-docs/stable/reference/api/pandas.DataFrame.html>`_
    :type variables: list
    :type actual: str
    :type expected: str
    :type inOrder: bool
    :type grouped: bool
    :ivar df: The Pandas dataframe containing underlying data
    :ivar var_list: Variables being optimized
    :ivar actual: The name of the Actual Incurred Claims column in df
    :ivar expected: The name of the Manual Expected Claims column in df
    :ivar levels: The dictionary containing all factor levels for all variables passed from `variables`
    """
    def __init__(self, df, variables, actual, expected, inOrder=True, grouped = False):
        self.df = df
        self.var_list = variables
        self.inOrder = inOrder
        self.grouped = grouped
        if inOrder:
            if self.grouped:
                print("WARNING: Setting grouped to False, doesn't make sense to run in order and grouped.")
                self.grouped = False
        self.actual = actual
        self.expected = expected
        self.__getLevels()
        self._initialAE = df[actual].sum()/df[expected].sum()
    def __getLevels(self):
        self.levels = {}
        #Putting factor levels into the dictionary
        for v in self.var_list:
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
    :ivar bounds_lower: Dictionary containing lower bounds for the factor changes based off of credibility.
    :ivar bounds_upper: Dictionary containing upper bounds for the factor changes based off of credibility.
    :ivar res: The OptimizeResult containing information on the Differential Evolution result. See `this page <https://docs.scipy.org/doc/scipy/reference/generated/scipy.optimize.OptimizeResult.html#scipy.optimize.OptimizeResult>`_ for more information.

            ** ``res`` Attributes**

            * ``x``: ``ndarray``
            The solution of the optimization.

            * ``success``: ``bool``
            Whether or not the optimizer exited successfully.

            * ``status``: ``int``
            Termination status of the optimizer. Its value depends on the underlying solver. Refer to message for details.

            * ``message``: ``str``
            Description of the cause of the termination.

            * ``fun``, ``jac``, ``hess``: ``ndarray``
            Values of objective function, its Jacobian and its Hessian (if available). The Hessians may be approximations, see the documentation of the function in question.

            * ``hess_inv``: ``object``
            Inverse of the objective function’s Hessian; may be an approximation. Not available for all solvers. The type of this attribute may be either np.ndarray or scipy.sparse.linalg.LinearOperator.

            * ``nfev``, ``njev``, ``nhev``: ``int``
            Number of evaluations of the objective functions and of its Jacobian and Hessian.

            * ``nit``: ``int``
            Number of iterations performed by the optimizer.

            * ``maxcv``: ``float``
            The maximum constraint violation.


    :type bounds_lower: dict
    :type bounder_upper: dict
    :type bounds: dict
    :type res: OptimizeResult



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
        self.niter = 0
        self.res = None

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
            for var in self.options.data.var_list:
                self.bounds_lower[var]=[0.8]*len(self.options.data.levels[var])
                self.bounds_upper[var]=[1.2]*len(self.options.data.levels[var])



    def __createCredibility(self):
        self.bounds_lower = {}
        self.bounds_upper = {}
        self.bounds = {}
        for v in self.options.data.var_list:
            lb = []
            ub = []
            x = 0
            self.bounds[v]={}
            for f in self.options.data.levels[v]:
                try:
                    credibility = np.sqrt(self.options.data.df.loc[self.options.data.df[v] == f, self.lifeYears].sum() / 400000)
                    AEratio = (self.options.data.df.loc[self.options.data.df[v] == f, self.options.data.actual].sum() / self.options.data.df.loc[
                        self.options.data.df[v] == f, self.options.data.expected].sum()) / (
                                          sum(self.options.data.df[self.options.data.actual]) / sum(
                                      self.options.data.df[self.options.data.expected]))
                    bound = AEratio * credibility + (1 - credibility)
                    if bound < 1:
                        self.bounds[v][f]=[1,max(0.9,bound)]
                        ub.append(1)
                        lb.append(max(0.9,bound))
                    if bound >= 1:
                        self.bounds[v][f]=[min(bound,1.1),1]
                        ub.append(min(bound,1.1))
                        lb.append(1)
                    if np.isnan(bound):
                        self.bounds[v][f]=[1,1]
                        ub.append(1)
                        lb.append(1)
                except(RuntimeWarning):
                    raise RuntimeWarning("Unexpected value in "+str(v)+" - "+str(f)+". Hint: Check for nulls or 0 Life Years.")
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

        if new_AE < self.options.data._initialAE * 0.95 or new_AE > self.options.data._initialAE * 1.05:
            abs_dev += 1e10
        self.niter += 1
        if self.niter % 100 == 0:
            print("Just finished deviation evaluation #:",self.niter)
        return abs_dev

    def __change_manual_expected(self, factorlist, factor):
        factor_dict = {}
        for i in range(len(self.options.data.levels[factor])):
            factor_dict[self.options.data.levels[factor][i]] = factorlist[i]
        self.options.data.df[self.options.data.expected] = self.options.data.df[self.options.data.expected]\
                                                         * self.options.data.df[factor].map(factor_dict)

    def __abs_dev_inOrder(self, factorlist):
        """
        :param factorlist: The current set of factors for the given variables.
        :return abs_dev: The resulting sum of absolute deviations of Actual vs Expected across all policies for the given factorlist.
        """
        variables = self.options.data.var_list
        global factor_dict
        factor_dict = {}
        overall = 0
        for v in variables:
            factor_dict[v]={}
            for i in range(len(self.options.data.levels[v])):
                factor_dict[v][self.options.data.levels[v][i]] = factorlist[overall]
                overall += 1
        self.options.data.df["new_exp_weighted_factors"]=1
        for var in variables:
            self.options.data.df["new_exp_weighted_factors"]=self.options.data.df["new_exp_weighted_factors"]*\
                                                             self.options.data.df[var].map(factor_dict[var])
        new_exp_weighted = sum(self.options.data.df[self.options.data.expected]*self.options.data.df["new_exp_weighted_factors"])

        new_AE = sum(self.options.data.df[self.options.data.actual].values) / new_exp_weighted
        abs_dev = sum(
            abs(self.options.data.df[self.options.data.expected]*self.options.data.df["new_exp_weighted_factors"] *
                new_AE - self.options.data.df[self.options.data.actual].values))
        if new_AE < self.options.data._initialAE * 0.95 or new_AE > self.options.data._initialAE * 1.05:
            abs_dev += 1e10
        self.niter += 1
        if self.niter % 100 == 0:
            print("Just finished deviation evaluation #:",self.niter)
        return abs_dev


    def __abs_dev_grouped(self, factorlist):
        """
        :param factorlist: The current set of factors for the given variables.
        :return abs_dev: The resulting sum of absolute deviations of Actual vs Expected across all policies for the given factorlist.
        """


        variables = self.options.data.var_list
        global factor_dict
        factor_dict = {}
        overall = 0
        expecteds = []
        actuals = []
        for v in variables:
            factor_dict[v]={}
            for i in range(len(self.options.data.levels[v])):
                factor_dict[v][self.options.data.levels[v][i]] = factorlist[overall]
                overall += 1
        self.options.data.df["new_exp_weighted_factors"]=1

        for var in variables:
            self.options.data.df["new_exp_weighted_factors"]=self.options.data.df["new_exp_weighted_factors"]*\
                                                             self.options.data.df[var].map(factor_dict[var])

        self.options.data.df["new_exp_weighted_AO"] = self.options.data.df[self.options.data.expected]*self.options.data.df["new_exp_weighted_factors"]
        new_exp_weighted = self.options.data.df["new_exp_weighted_AO"].sum()
        for var in variables:
            expecteds = np.append(expecteds,(self.options.data.df["new_exp_weighted_AO"].groupby(self.options.data.df[var])).sum())
            actuals = np.append(actuals,(self.options.data.df[self.options.data.actual].groupby(self.options.data.df[var])).sum())

        new_AE = sum(self.options.data.df[self.options.data.actual].values) / new_exp_weighted

        abs_dev = sum(abs(expecteds*new_AE - actuals))
        if new_AE < self.options.data._initialAE * 0.95 or new_AE > self.options.data._initialAE * 1.05:
            abs_dev += 1e10
        self.niter += 1
        if self.niter % 100 == 0:
            print("Just finished deviation evaluation #:",self.niter)
        return abs_dev



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

        print("Starting AE", sum(self.options.data.df[self.options.data.actual])/sum(self.options.data.df[self.options.data.expected]))

        if self.options.data.inOrder: #Meaning to optimize sequentially
            print("Starting absolute deviation: ", start_dev)
            print("Starting optimization date and time: ", time.asctime(time.localtime(time.time())))
            print("__________________________________________________________")

            current = 1
            for f in self.options.data.var_list:
                print("Currently working on "+f+", variable "+str(current)+"/"+str(len(self.options.data.var_list))+".")
                print("Absolute Deviation before working on "+f+": "+ str(sum(abs(self.options.data.df[self.options.data.expected].values *
                                sum(self.options.data.df[self.options.data.actual].values) /
                                sum(self.options.data.df[self.options.data.expected].values)
                                - self.options.data.df[self.options.data.actual].values))))
                current += 1
                xmin = self.bounds_lower[f]
                xmax = self.bounds_upper[f]
                bounds = [(low, high) for low, high in zip(xmin, xmax)]

                self.res = scipy.optimize.differential_evolution(self.__abs_dev, bounds = bounds, args = (f,),
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
                self.__change_manual_expected(self.res.x, f)
                print("Absolute Deviation after working on "+f+": "+ str(self.res.fun))
                print("==========================================================")

            endingAE = sum(self.options.data.df[self.options.data.actual])/sum(self.options.data.df[self.options.data.expected])
            endingdev = self.res.fun
            print(self.res.message)
            print("Ending optimization date and time",time.asctime( time.localtime(time.time()) ))

            return final_dict, endingAE, endingdev

        if not self.options.data.inOrder:#Meaning to optimize all at once
            if self.options.data.grouped:


                actuals = []
                expecteds = []
                for var in self.options.data.var_list:
                    expecteds = np.append(expecteds, (
                        self.options.data.df[self.options.data.expected].groupby(self.options.data.df[var])).sum())
                    actuals = np.append(actuals, (
                        self.options.data.df[self.options.data.actual].groupby(self.options.data.df[var])).sum())


                abs_dev = abs(expecteds * self.options.data._initialAE - actuals).sum()
                print("Starting absolute deviation: ", abs_dev)
                print("Starting optimization date and time: ", time.asctime(time.localtime(time.time())))
                print("__________________________________________________________")


                xmin = []
                xmax = []
                for var in self.options.data.var_list:
                    xmin.extend(self.bounds_lower[var])
                    xmax.extend(self.bounds_upper[var])
                bounds = [(low, high) for low, high in zip(xmin, xmax)]
                print("Calculating... please wait")
                self.res = scipy.optimize.differential_evolution(self.__abs_dev_grouped, bounds = bounds,
                                                            strategy = self.options.strategy,
                                                            maxiter = self.options.maxiter,
                                                            popsize = self.options.popsize, tol = self.options.tol,
                                                            mutation = self.options.mutation,
                                                            recombination = self.options.recombination,
                                                            seed = self.options.seed, callback = self.options.callback,
                                                            disp = self.options.disp, polish = self.options.polish,
                                                            init = self.options.init, atol = self.options.atol,
                                                            updating = self.options.updating,
                                                            workers = self.options.workers)

                final_dict = {}
                counter = 0
                for key in self.options.data.levels.keys():
                    final_dict[key] = {}
                    for level in self.options.data.levels[key]:
                        final_dict[key][level] = self.res.x[counter]
                        counter += 1
                endingAE = sum(self.options.data.df[self.options.data.actual]) / sum(
                    self.options.data.df[self.options.data.expected] * self.options.data.df["new_exp_weighted_factors"])
                endingdev = self.res.fun
                print(self.res.message)
                print("Ending optimization date and time", time.asctime(time.localtime(time.time())))

                return final_dict, endingAE, endingdev
            if not self.options.data.grouped:
                print("Starting absolute deviation: ", start_dev)
                print("Starting optimization date and time: ", time.asctime(time.localtime(time.time())))
                print("__________________________________________________________")

                xmin = []
                xmax = []
                for var in self.options.data.var_list:
                    xmin.extend(self.bounds_lower[var])
                    xmax.extend(self.bounds_upper[var])
                bounds = [(low, high) for low, high in zip(xmin, xmax)]
                print("Calculating... please wait")
                self.res = scipy.optimize.differential_evolution(self.__abs_dev_inOrder, bounds = bounds,
                                                            strategy = self.options.strategy,
                                                            maxiter = self.options.maxiter,
                                                            popsize = self.options.popsize, tol = self.options.tol,
                                                            mutation = self.options.mutation,
                                                            recombination = self.options.recombination,
                                                            seed = self.options.seed, callback = self.options.callback,
                                                            disp = self.options.disp, polish = self.options.polish,
                                                            init = self.options.init, atol = self.options.atol,
                                                            updating = self.options.updating,
                                                            workers = self.options.workers)

                final_dict = {}
                counter = 0
                for key in self.options.data.levels.keys():
                    final_dict[key]={}
                    for level in self.options.data.levels[key]:
                        final_dict[key][level]=self.res.x[counter]
                        counter += 1
                endingAE = sum(self.options.data.df[self.options.data.actual])/sum(self.options.data.df[self.options.data.expected]*self.options.data.df["new_exp_weighted_factors"])
                endingdev = self.res.fun
                print(self.res.message)
                print("Ending optimization date and time",time.asctime( time.localtime(time.time()) ))

                return final_dict, endingAE, endingdev



