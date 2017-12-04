# -*- coding: utf-8 -*-
"""
Created on July 2017

@author: Nicolas
"""

import numpy as np
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

# Cathedral points for each steps
steps = [100, 600, 2600, 3100, 5600, 6800,
         8300, 9800, 10300, 10800, 11300, 12000]
         
# Minimal yearly income to build cathedral
cathedralIncome = 100

#%%

# OPUS FRANCIGENUM

#TODO : Get the date of the global flag
ofYear = 1097

#TODO : Analyze the title flag repaired_cathedral

#%%

dfTitleVar = pd.read_csv(dataDir + savePrefix + "TitleVariables.csv")
dfChar = pd.read_csv(dataDir + savePrefix + "CharacterStats.csv")
dfArtFlag = pd.read_csv(dataDir + savePrefix + "ArtifactFlags.csv")
dfArtStats = pd.read_csv(dataDir + savePrefix + "ArtifactStats.csv")

#%%

cathedral = dfTitleVar[dfTitleVar["variable"] == "cathedral"]

#%%

print("Holdings which build Cathedral")
print(cathedral["title"].unique())

#%%

#TODO : Analyze the cathedral province modifiers

#TODO : Analyze the relic disparition

#%%

################## ANALYZE INCOMES OF RELIC OWNERS ############################
dfRelics = pd.merge(dfArtFlag[dfArtFlag["flag"]=="relique"], dfArtStats, on="artifact")
dfRelicAndIncome = pd.merge(dfRelics,
                            dfChar[["character", "Estimated year income", "year"]],
left_on=["owner", "year"], right_on=["character", "year"])
print("{0} unique relics".format(dfRelicAndIncome.type.unique().size))

#%%

relicsByType = pd.DataFrame()
for artType in dfRelicAndIncome["type"].unique():
    relicsByType = pd.concat([relicsByType,
                             dfRelicAndIncome.loc[dfRelicAndIncome["type"] == artType,
                                                  ["year","Estimated year income"]]
                                                  .set_index("year")
                                                  .rename(columns={"Estimated year income":artType})], axis=1)

#%%

fig, ax = plt.subplots(nrows=1, ncols=1, figsize=(width, height), dpi=dpi)
ax.set_title(u"Income of relic owners (Opus Francigenum {0})".format(ofYear),
             fontsize=20)
relicsByType.plot(ax=ax, fontsize=20, lw=2)
ax.axhline(cathedralIncome, color="black", linestyle='--')
plt.legend(loc=2, fontsize = 'x-large')
plt.savefig(imageDir + savePrefix + "RelicOwnerIncome.png", dpi=dpi)

#%%

############## ANALYZE THE CATHEDRAL BUILDING EVOLUTION #######################
cathedralByYear = pd.DataFrame()
for year in cathedral["year"].unique():
    cathedralByYear = pd.concat([cathedralByYear,
                                 cathedral.loc[cathedral["year"] == year,
                                               ["title","value"]]
                                               .set_index("title")
                                               .rename(columns={'value':year})], axis=1)
    

#%%

fig, ax = plt.subplots(nrows=1, ncols=1, figsize=(width, height), dpi=dpi)
ax.set_title(u"Cathedral evolution (Opus Francigenum {0})".format(ofYear),
             fontsize=20)
cathedralByYear.transpose().plot(ax=ax, fontsize=20, lw=2)
for i in range(len(steps)):
    ax.axhline(steps[i], color="black", linestyle='--')
plt.legend(loc=2, fontsize = 'x-large')
plt.savefig(imageDir + savePrefix + "Cathedral.png", dpi=dpi)

#%%

# Delta computation
cathedralDeltaByYear = cathedralByYear[cathedralByYear.columns[1:]].copy()
for iCol in range(1, cathedralByYear.columns.size):
    prevYear = cathedralByYear.columns[iCol - 1]
    year = cathedralByYear.columns[iCol]
    cathedralDeltaByYear[year] = (cathedralByYear[year] - cathedralByYear[prevYear]) / (year - prevYear)
    
#%%

fig, ax = plt.subplots(nrows=1, ncols=1, figsize=(width, height), dpi=dpi)
ax.set_title(u"Yearly Cathedral evolution (Opus Francigenum {0})".format(ofYear),
             fontsize=20)
cathedralDeltaByYear.transpose().plot(ax=ax, fontsize=20, lw=2)
plt.legend(loc=2, fontsize = 'x-large')
plt.savefig(imageDir + savePrefix + "CathedralIncreasing.png", dpi=dpi)

#%%
print("Mean of yearly evolution")
print(cathedralDeltaByYear.transpose().mean())

print("\nEstimation of the number of year to complete the cathedral")
print(12000/cathedralDeltaByYear.transpose().mean())

#%%

######################## ANALYZE THE ARTISTS ##################################
dfTraits = pd.read_csv(dataDir + savePrefix + "Traits.csv")

#%%

artists = dfTraits[(dfTraits['trait'] >= 329) & (dfTraits['trait'] <= 338)]

#%%

sculptor = artists[(artists['trait'] >= 329) & (artists['trait'] <= 331)]
painter = artists[(artists['trait'] >= 332) & (artists['trait'] <= 335)]
glassMaker = artists[(artists['trait'] >= 336) & (artists['trait'] <= 338)]

#%%

artistsByType = pd.DataFrame()
artistsByType['year'] = np.arange(min(artists['year']), max(artists['year']))

#%%
artistsByType = pd.merge(artistsByType,
         pd.DataFrame(sculptor.groupby('year').count().character)
         .reset_index(), on='year', how='left')
artistsByType = pd.merge(artistsByType,
         pd.DataFrame(painter.groupby('year').count().character)
         .reset_index(), on='year', how='left')
artistsByType = pd.merge(artistsByType,
         pd.DataFrame(glassMaker.groupby('year').count().character)
         .reset_index(), on='year', how='left')
artistsByType.columns = ['year', 'sculptor', 'painter', 'glassMaker']
artistsByType.set_index('year', inplace=True)


#%%

fig, ax = plt.subplots(nrows=1, ncols=1, figsize=(width, height), dpi=dpi)
ax.set_title(u"Artists", fontsize=20)
artistsByType.plot(ax=ax, fontsize=20, lw=2)
plt.legend(loc=2, fontsize = 'x-large')
plt.savefig(imageDir + savePrefix + "ArtistsByType.png", dpi=dpi)

#%%

apprentices = artists[artists['trait'].isin([329, 332, 336])]
apprenticesByType = pd.DataFrame()
apprenticesByType['year'] = np.arange(min(apprentices['year']), max(apprentices['year']))

#%%

apprenticesByType = pd.merge(apprenticesByType,
         pd.DataFrame(apprentices[apprentices['trait'] == 329].groupby('year')
         .count().character).reset_index(), on='year', how='left')
apprenticesByType = pd.merge(apprenticesByType,
         pd.DataFrame(apprentices[apprentices['trait'] == 332].groupby('year')
         .count().character).reset_index(), on='year', how='left')
apprenticesByType = pd.merge(apprenticesByType,
         pd.DataFrame(apprentices[apprentices['trait'] == 336].groupby('year')
         .count().character).reset_index(), on='year', how='left')
apprenticesByType.columns = ['year', 'sculptor', 'painter', 'glassMaker']
apprenticesByType.set_index('year', inplace=True)

#%%

fig, ax = plt.subplots(nrows=1, ncols=1, figsize=(width, height), dpi=dpi)
ax.set_title(u"Apprentices", fontsize=20)
apprenticesByType.plot(ax=ax, fontsize=20, lw=2)
plt.legend(loc=2, fontsize = 'x-large')
plt.savefig(imageDir + savePrefix + "ApprenticesByType.png", dpi=dpi)
