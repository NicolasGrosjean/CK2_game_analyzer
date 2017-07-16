# -*- coding: utf-8 -*-
"""
Created on Sat Jun 24 11:20:58 2017

@author: Nicolas
"""

import pandas as pd
import matplotlib.pyplot as plt
import matplotlib
matplotlib.style.use('ggplot')

#%%

dataDir = "../save_parser/results/"
imageDir = "./images/"

#%%

# Image resolution
width = 16
height = 9

# Multiplication of previous ones by dpi to have pixel resolution
dpi = 100 

#%%

dfTitleVar = pd.read_csv(dataDir + "TitleVariables.csv")

#%%

dev = dfTitleVar[dfTitleVar["variable"] == "developpement"]

#%%
print("Number of titles by year")
print(dev.groupby("year").count().title)

#%%
minYear = min(dev["year"])
maxYear = max(dev["year"])

print("Top 10 of more develelopped holdings in {0}".format(minYear))
top = dev.loc[dev["year"]==minYear, ["title", "value"]].sort_values("value", ascending=False).head(10)
top.index = range(1,11)
print(top)
print("")
print("Top 10 of more develelopped holdings in {0}".format(maxYear))
top = dev.loc[dev["year"]==maxYear, ["title", "value"]].sort_values("value", ascending=False).head(10)
top.index = range(1,11)
print(top)

#%%
print("Evolution of the negative development")
print(dev[dev["value"] < 0].sort_values("year"))

#%%

devByYear = pd.DataFrame()
for year in dev["year"].unique():
    devByYear = pd.concat([devByYear, dev.loc[dev["year"] == year, ["title","value"]].set_index("title").rename(columns={'value':year})], axis=1)

#%%

quantiles = devByYear.quantile([.1, .5, .9])
quantiles.rename(index={.1:"Q10", .5:"Median", .9:"Q90"}, inplace=True)
mini = pd.DataFrame(devByYear.min(), columns=["Min"]).transpose()
maxi = pd.DataFrame(devByYear.max(), columns=["Max"]).transpose()
devStats = pd.concat([mini, quantiles, maxi], axis=0)

#%%

fig, ax = plt.subplots(nrows=1, ncols=1, figsize=(width, height), dpi=dpi)
ax.set_title(u"Development evolution ({0} - {1})".format(minYear,
             devStats.columns[devStats.shape[1] - 1]), fontsize=20)
devStats.transpose().plot(ax=ax, fontsize=20, lw=2)
plt.legend(loc=2, fontsize = 'x-large')
plt.savefig(imageDir + "Developpement.png", dpi=dpi)
