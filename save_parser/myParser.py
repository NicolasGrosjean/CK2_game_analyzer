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

#%%
def unspaced(string):
    return string.replace(' ', '').replace('\t', '').replace('\n', '')

#%%
# TODO : Parse flag and modifiers
def parseProvinceVariable(it, init, n):
    """
    Parse the the provinces of a CK2 save game
    
    :param it: iterator of the lines when we are at the province key
    :param init: current line number
    :param n: number of lines in the file
    :return: list of provinces variables
    :rtype: dictionnary
    """
    res = list()
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
                province = tokens[0]
            if isVariable:
                res.append({"province":province, "variable":tokens[0],
                            "value":tokens[1]})
            if (deep == 3) & (variableKey in line):
                isVariable = True
    return res

#%%

def parse(lines):
    """
    Parse the lines of a CK2 savegame file
    
    :return: (provVar)
    """
    endParsing = False
    n = len(lines)
    i = 0
    it = iter(lines)
    while (not endParsing) & (i < n):
        i += 1
        line = next(it)
        if provinceKey in line:
            endParsing = True
            while ((not '{' in line) & (i < n)):
                line = next(it)
            provVar = parseProvinceVariable(it, i, n)
    return (provVar)

#%%

def getYearFromFileName(fileName):
    parts = fileName.split('.')
    if len(parts) > 1:
        name = parts[0]
        parts = name.split('_')
        return parts[len(parts) - 1]
    return None

#%%

# TODO : Filter on the save name
filesToParse = os.listdir(saveDir)
print("{} files to parse".format(len(filesToParse)))

#%%

first = True
for fileName in filesToParse:
    year = getYearFromFileName(fileName)
    if year == None :
        continue
    readFile = io.open(saveDir + fileName, 'rt', 1, 'latin_1')
    lines = readFile.readlines()
    readFile.close()
    (provVar) = parse(lines)
    dfYear = pd.DataFrame(provVar)
    dfYear["year"] = year
    if first:
        df = dfYear
        first = False
    else:
        df = pd.concat([df, dfYear], axis=0)
    print("Year {} treated!".format(year))
        
#%%

# TODO : add the save name to the file
# TODO : update the file instead of create one
df.to_csv(targetDir + "ProvinceVariables.csv", index=False)

