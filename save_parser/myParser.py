# -*- coding: utf-8 -*-
"""
Created on Tue Jun 20 21:12:34 2017

@author: Nicolas
"""

import os
import io
import pandas as pd

#%%  

saveDir = "../save_archiver/saves/"
targetDir = "./results/"

#%%
provinceKey = "provinces="
variableKey = "variables="
titleKey = "title="
modifierToken = "modifier"

#%%
def unspaced(string):
    return string.replace(' ', '').replace('\t', '').replace('\n', '').replace('\"', '')

#%%
# TODO : Parse flags
def parseScopeVariable(it, init, n, scopeType):
    """
    Parse the scopes of a CK2 save game
    
    :param it: iterator of the lines when we are at the province key
    :param init: current line number
    :param n: number of lines in the file
    :param scopeType: name of the scope type
    :return: list of scope variables, modified it and init
    :rtype: (variable dictionnary, modifier dictionnary, iterator, int)
    """
    var = list()
    mod = list()
    i = init    

    deep = 2 # deep 0 = root, 1 = provinces
    isVariable = False
    while (deep > 1) & (i < n):
        i += 1
        line = unspaced(next(it))
        if '{' in line:
            deep += 1
        if '}' in line:
            deep -= 1
            isVariable = False
        tokens = line.split('=')
        if len(tokens) == 2:
            if deep == 2 :
                scope = tokens[0]
            if isVariable:
                var.append({scopeType:scope, "variable":tokens[0],
                            "value":tokens[1]})
            if (deep == 3) & (variableKey in line):
                isVariable = True
            if (tokens[0] == modifierToken) & (tokens[1] != ''):
                mod.append({scopeType:scope, "modifier":tokens[1]})
    return (var, mod, it, i)

#%%

def parse(lines):
    """
    Parse the lines of a CK2 savegame file
    
    :return: (provVar, provMod, titleVar)
    """
    provinceFound = False
    titleFound = False
    n = len(lines)
    i = 0
    it = iter(lines)
    while (not titleFound) & (i < n):
        i += 1
        line = next(it)
        if provinceKey in line:
            provinceFound = True
            while ((not '{' in line) & (i < n)):
                i += 1
                line = next(it)
            (provVar, provMod, it, i) = parseScopeVariable(it, i, n, "province")
        if provinceFound & (titleKey in line):
            titleFound = True
            while ((not '{' in line) & (i < n)):
                i += 1
                line = next(it)
            (titleVar, titleMod, it, i) = parseScopeVariable(it, i, n, "title")
    return (provVar, provMod, titleVar)

#%%

def getYearFromFileName(fileName):
    parts = fileName.split('.')
    if len(parts) > 1:
        name = parts[0]
        parts = name.split('_')
        return parts[len(parts) - 1]
    return None
    
#%%
def createOrConcatDataFrame(dictionnary, df):
    """
    Create a dataframe or concatenate with df from a dictionnary
    
    :param dictionnary:
    :param df: if len(df) == 0 then create the dataframe, otherwise concatenate with it
    :return: dataframe
    """
    dfYear = pd.DataFrame(dictionnary)
    dfYear["year"] = year
    if len(df) == 0:
        df = dfYear
    else:
        df = pd.concat([df, dfYear], axis=0)
    return df

#%%

# TODO : Filter on the save name
filesToParse = os.listdir(saveDir)
print("{} files to parse".format(len(filesToParse)))

#%%

dfProvVar = pd.DataFrame()
dfProvMod = pd.DataFrame()
dfTitleVar = pd.DataFrame()
for fileName in filesToParse:
    # Get the year
    year = getYearFromFileName(fileName)
    if year == None :
        continue
    
    # Get the lines
    readFile = io.open(saveDir + fileName, 'rt', 1, 'latin_1')
    lines = readFile.readlines()
    readFile.close()
    
    # Parse
    (provVar, provMod, titleVar) = parse(lines)
    
    # Data consolidation
    dfProvVar = createOrConcatDataFrame(provVar, dfProvVar)
    dfProvMod = createOrConcatDataFrame(provMod, dfProvMod)
    dfTitleVar = createOrConcatDataFrame(titleVar, dfTitleVar)
  
    print("Year {} treated!".format(year))
    
#%%
    
# Column ordering
dfProvMod = dfProvMod[["province", "modifier", "year"]]
        
#%%

# TODO : add the save name to the file
# TODO : update the fileq instead of create them
dfProvVar.to_csv(targetDir + "ProvinceVariables.csv", index=False)
dfProvMod.to_csv(targetDir + "ProvinceModifiers.csv", index=False)
dfTitleVar.to_csv(targetDir + "TitleVariables.csv", index=False)

