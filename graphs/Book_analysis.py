# -*- coding: utf-8 -*-
"""
Created on October 2017

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

bookTypes= ["science_book", "economy_book", "litteracy_book", ]

#%%

dfArtFlag = pd.read_csv(dataDir + savePrefix + "ArtifactFlags.csv")
dfArtStats = pd.read_csv(dataDir + savePrefix + "ArtifactStats.csv")

#%%

####################### ANALYZE BOOK NUMBER #################################
dfBookz = pd.merge(dfArtFlag[dfArtFlag["flag"]=="bookz"], dfArtStats, on="artifact")
dfUniqueBook = pd.merge(dfArtFlag[dfArtFlag["flag"]=="unique_book"], dfArtStats, on="artifact")
dfUsedBook = pd.merge(dfArtFlag[dfArtFlag["flag"]=="used_book"], dfArtStats, on="artifact")

#%%

fig, ax = plt.subplots(nrows=1, ncols=1, figsize=(width, height), dpi=dpi)
ax.set_title(u"Number of bookz in the game", fontsize=20)
dfBookz.groupby("year").count().flag.plot(ax=ax, fontsize=20, lw=2)
plt.savefig(imageDir + savePrefix + "BookZNumber.png", dpi=dpi)

#%%

fig, ax = plt.subplots(nrows=1, ncols=1, figsize=(width, height), dpi=dpi)
ax.set_title(u"Number of unique books in the game", fontsize=20)
dfUniqueBook.groupby("year").count().flag.plot(ax=ax, fontsize=20, lw=2)
plt.savefig(imageDir + savePrefix + "UniqueBook.png", dpi=dpi)

#%%
dfUniqueBookTypeYear = pd.DataFrame()
group = dfUniqueBook.groupby(["year", "type"]).count().flag.reset_index()
for year in dfUniqueBook["year"].unique():
    dfUniqueBookTypeYear = pd.concat([dfUniqueBookTypeYear,
                                      group.loc[group["year"] == year,
                                                ["type", "flag"]]
                                              .set_index("type")
                                              .rename(columns={"flag":year})],
                                      axis=1)

#%%

fig, ax = plt.subplots(nrows=1, ncols=1, figsize=(width, height), dpi=dpi)
ax.set_title(u"Number of unique books in the game by type", fontsize=20)
dfUniqueBookTypeYear.transpose().fillna(0).plot(ax=ax, fontsize=20, lw=2)
plt.legend(loc=2, fontsize = 'x-large')
plt.savefig(imageDir + savePrefix + "UniqueBookType.png", dpi=dpi)

#%%

fig, ax = plt.subplots(nrows=1, ncols=1, figsize=(width, height), dpi=dpi)
ax.set_title(u"Number of used books in the game (do not count destroyed books)", fontsize=20)
dfUsedBook.groupby("year").count().flag.plot(ax=ax, fontsize=20, lw=2)
plt.savefig(imageDir + savePrefix + "UsedBook.png", dpi=dpi)

#%%

maxYear = max(dfBookz.year)
dfBookTypes = pd.DataFrame()
for bookType in bookTypes:
    dfBookType = pd.merge(dfArtFlag[dfArtFlag["flag"] == bookType],
                            dfArtStats[dfArtStats["year"] == maxYear], on="artifact")
    dfBookTypes = pd.concat([dfBookTypes, pd.DataFrame([[bookType, dfBookType.shape[0]]], columns=["type", "nb"])])
dfBookTypes = dfBookTypes.set_index("type")

#%%
fig, ax = plt.subplots(nrows=1, ncols=1, figsize=(width, height), dpi=dpi)
ax.set_title(u"Number books by type in {0}".format(maxYear), fontsize=20)
dfBookTypes["nb"].plot.pie(ax=ax, fontsize=20, labels=dfBookTypes.index,
           autopct=lambda(p): '{:.0f}'.format(p * np.sum(dfBookTypes["nb"]) / 100))
plt.savefig(imageDir + savePrefix + "BookByType.png", dpi=dpi)
