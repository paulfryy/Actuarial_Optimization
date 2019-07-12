import sys
import pandas as pd
import numpy as np



import ManualOptimization as mo

mydata = pd.read_excel("//prdenffs01/L&DI-Actuarial/Actuarial/LTD Rate Refresh/2019/LTD R Group 6-28 Compare factors.xlsx", sheet_name= "Current Factors")
mydata=mydata.dropna(subset=["Manual_Expected_weighted"])
mydata=mydata.dropna(subset=["SIC_Group_LDI"])
mydata = mydata.loc[mydata["Hybrid_Indicator"] == 0]
mydata = mydata.loc[mydata["Year"] >= 2014]
mydata = mydata.reset_index()


dataClass = mo.Data(mydata, ['SIC_Group_LDI', 'SG_Partic', 'SG_CaseSize', 'SG_Blue_Pct', 'SG_Avg_Salary'], actual = "Incurred_Claim_Amount_weighted",
                   expected = "Manual_Expected_weighted")


myOptions = mo.Options(dataClass, maxiter=1000000)
myOptimize = mo.Optimize(myOptions, credibility= True, lifeYears= "Life_Years")
a, b, c = myOptimize.run()
print(a)
print(b)
print(c)


