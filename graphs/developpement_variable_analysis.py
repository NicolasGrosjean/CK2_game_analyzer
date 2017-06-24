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
resolutionWidth = 14.4
resolutionHeight = 9

#%%

dfTitleVar = pd.read_csv(dataDir + "TitleVariables.csv")

#%%

dev = dfTitleVar[dfTitleVar["variable"] == "developpement"]

#%%
print("Number of titles by year")
dev.groupby("year").count().title

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

fig, ax = plt.subplots(nrows=1, ncols=1)
ax.set_title(u"Development evolution ({0} - {1})".format(devStats.columns[0],
             devStats.columns[devStats.shape[1] - 1]))
fig.set_size_inches(resolutionWidth, resolutionHeight)
devStats.transpose().plot(ax=ax)
plt.savefig(imageDir + "Developpement.png")
