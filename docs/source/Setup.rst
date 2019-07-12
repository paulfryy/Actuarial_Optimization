.. _Setup:


Setup
=====

This page is to be used as a starting guide, giving explanations of data needed.


Data
####

To start, data needs to be brought into an importable file. The easiest is an excel file through the use of SQL. The column names can vary,
but certain values must be represented.

Columns
*******

Most of the columns can vary, but each dataset will need to contain a certain set of columns.

* The data needs to have a `Manual Expected` column (weighted or unweighted). This value is calculated as follows: :math:`\text{Manual_Premium} \times \text{PLR} \times (1-\text{Credibility})`. `Manual_Premium` is just the current manual rate, `PLR` is the Permissable Loss Ratio, and Credibility is the policy/grouping/sector's credibility, based on life years (**Note: Weighted refers to multiplying by (1-Credibility) like above**).

* The data must also include an `Incurred Claim Amount` column (weighted or unweighted).This value can be calulated by: :math:`\text{Incurred Claim Amount}\times(1-\text{Credibiliy})`.  The `Incurred Claim Amount` is just the historical incurred claim amount for the sector/policy/grouping. (**Note: Weighted refers to multiplying by (1-Credibility) like above**).

* **Optional** A `Life Years` column, representing the sum of life years covered by the policy/sector/grouping. This is used to set up the credibility for the bounds of the evolutionary algorithm. If not used, default settings will be applied. See :ref:`this page<ACTOPT>` for more details.
