# -*- coding: utf-8 -*-
"""
Created on June 2017

@author: Nicolas
"""

import pandas as pd
import matplotlib.pyplot as plt
import matplotlib
matplotlib.style.use('ggplot')

#%%

dataDir = "../save_parser/results/"
imageDir = "../graphs/images/"

#%%

savePrefix = "save_test_"

#%%

# Image resolution
width = 19.2
height = 10.8

# Multiplication of previous ones by dpi to have pixel resolution
dpi = 100 

#%%

# Steps for population buildings
castleSteps = [100, 150, 200, 250, 350]
citySteps   = [100, 150, 250, 400, 500]
templeSteps = [100, 170, 220, 260, 300]

#%%

dfTitleVar = pd.read_csv(dataDir + savePrefix + "TitleVariables.csv")

#%%

dev = dfTitleVar[dfTitleVar["variable"] == "developpement"]

#%%
print("Number of titles by year")
print(dev.groupby("year").count().title)

#%%
minYear = min(dev["year"])
maxYear = max(dev["year"])

print("Top 10 of more developped holdings in {0}".format(minYear))
top = dev.loc[dev["year"]==minYear, ["title", "value"]].sort_values("value", ascending=False).head(10)
top.index = range(1,11)
print(top)
print("")
print("Top 10 of more developped holdings in {0}".format(maxYear))
top = dev.loc[dev["year"]==maxYear, ["title", "value"]].sort_values("value", ascending=False).head(10)
top.index = range(1,11)
print(top)

#%%
print("Evolution of the negative development")
print(dev[dev["value"] < 0].sort_values("year"))

#%%

def createStatDataFrame(df):
    """
    Create a statistic (min, Q10, median, Q90n, max) dataframe from a dataframe
    with "year", "title" and "value" columns
    """
    devByYear = pd.DataFrame()
    for year in df["year"].unique():
        devByYear = pd.concat([devByYear, df.loc[df["year"] == year, ["title","value"]].set_index("title").rename(columns={'value':year})], axis=1)
    quantiles = devByYear.quantile([.1, .5, .9])
    quantiles.rename(index={.1:"Q10", .5:"Median", .9:"Q90"}, inplace=True)
    mini = pd.DataFrame(devByYear.min(), columns=["Min"]).transpose()
    maxi = pd.DataFrame(devByYear.max(), columns=["Max"]).transpose()
    devStats = pd.concat([mini, quantiles, maxi], axis=0)
    return devStats

#%%

##################### GLOBAL DEVELOPMENT STATS ################################

devStats = createStatDataFrame(dev)

#%%

fig, ax = plt.subplots(nrows=1, ncols=1, figsize=(width, height), dpi=dpi)
ax.set_title(u"Development evolution ({0} - {1})".format(minYear,
             devStats.columns[devStats.shape[1] - 1]), fontsize=20)
devStats.transpose().plot(ax=ax, fontsize=20, lw=2)
plt.legend(loc=2, fontsize = 'x-large')
plt.savefig(imageDir + savePrefix + "Developpement.png", dpi=dpi)

#%%

################# DEVELOPMENT STATS BY HOLDING TYPE############################

dfTitleTyp = pd.read_csv(dataDir + "TitleTypes.csv")

#%%

dfCastle = pd.merge(dev, dfTitleTyp[dfTitleTyp["type"] == "castle"], on="title")
dfCity = pd.merge(dev, dfTitleTyp[dfTitleTyp["type"] == "city"], on="title")
dfTemple = pd.merge(dev, dfTitleTyp[dfTitleTyp["type"] == "temple"], on="title")

#%%

dfCastleStats = createStatDataFrame(dfCastle)
dfCityStats = createStatDataFrame(dfCity)
dfTempleStats = createStatDataFrame(dfTemple)

#%%

fig, ax = plt.subplots(nrows=1, ncols=1, figsize=(width, height), dpi=dpi)
ax.set_title(u"CASTLE development evolution ({0} - {1})".format(minYear,
             dfCastleStats.columns[dfCastleStats.shape[1] - 1]), fontsize=20)
dfCastleStats.transpose().plot(ax=ax, fontsize=20, lw=2)
for i in range(len(castleSteps)):
    ax.axhline(castleSteps[i], color="black", linestyle='--')
plt.legend(loc=2, fontsize = 'x-large')
plt.savefig(imageDir + savePrefix + "Castle_developpement.png", dpi=dpi)

#%%

fig, ax = plt.subplots(nrows=1, ncols=1, figsize=(width, height), dpi=dpi)
ax.set_title(u"CITY development evolution ({0} - {1})".format(minYear,
             dfCityStats.columns[dfCityStats.shape[1] - 1]), fontsize=20)
dfCityStats.transpose().plot(ax=ax, fontsize=20, lw=2)
for i in range(len(citySteps)):
    ax.axhline(citySteps[i], color="black", linestyle='--')
plt.legend(loc=2, fontsize = 'x-large')
plt.savefig(imageDir + savePrefix + "City_developpement.png", dpi=dpi)

#%%

fig, ax = plt.subplots(nrows=1, ncols=1, figsize=(width, height), dpi=dpi)
ax.set_title(u"TEMPLE development evolution ({0} - {1})".format(minYear,
             dfTempleStats.columns[dfTempleStats.shape[1] - 1]), fontsize=20)
dfTempleStats.transpose().plot(ax=ax, fontsize=20, lw=2)
for i in range(len(templeSteps)):
    ax.axhline(templeSteps[i], color="black", linestyle='--')
plt.legend(loc=2, fontsize = 'x-large')
plt.savefig(imageDir + savePrefix + "Temple_developpement.png", dpi=dpi)
