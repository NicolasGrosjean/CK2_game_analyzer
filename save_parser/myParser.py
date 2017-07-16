# -*- coding: utf-8 -*-
"""
Created on June 2017

@author: Nicolas
"""

import os
import io
import pandas as pd

#%%  

saveDir = "../save_archiver/saves/"
targetDir = "./results/"


#%%

extractedCharStats = list({"b_d", "d_d", "prs", "piety", "wealth", "emp",
                           "host", "emi", "eyi", "rel", "cul", "bn", "fat", "mot"})
charStatLib = {"b_d" : "Birth date", "d_d" : "Death date", "prs" :"Prestige",
               "piety": "Piety", "wealth" : "Wealth", "emp" : "Employer",
               "host" : "Host", "emi" : "Estimated month income",
               "eyi" : "Estimated year income", "rel" : "Religion",
               "cul" : "Culture", "bn" : "Birth Name", "fat" : "Father",
               "mot": "Mother"}

#%%
provinceKey = "provinces="
variableKey = "variables="
titleKey = "title="
characterKey = "character="
modifierToken = "modifier"

provinceScope = "province"
titleScope = "title"
charScope = "character"

#%%
def unspaced(string):
    return string.replace(' ', '').replace('\t', '').replace('\n', '').replace('\"', '')

#%%

def goodScopeModifier(deep, scopeType):
    if scopeType == provinceScope:
        return (deep == 4)
    if scopeType == titleScope:
        return (deep == 5)
    if scopeType == charScope:
        return (deep == 4)
            

#%%
# TODO : Parse flags
def parseScope(it, init, n, scopeType):
    """
    Parse the scopes of a CK2 save game
    
    :param it: iterator of the lines when we are at the province key
    :param init: current line number
    :param n: number of lines in the file
    :param scopeType: name of the scope type
    :return: list of scope variables, modified it and init
    :rtype: (variable dictionnary, modifier dictionnary, iterator, int,
             title type dictionnary, character stats)
    """
    var = list()
    mod = list()
    titTyp = list()
    charStats = list()
    i = init
    isProvince = (scopeType == provinceScope)
    isCharacter = (scopeType == charScope)

    deep = 2 # deep 0 = root, 1 = provinces
    isVariable = False # Is currently parsing a variable bloc
    isTitle = False # Is currently parsing a title bloc
    oneChar = None # Stats of oe character
    while (deep > 1) & (i < n):
        i += 1
        line = unspaced(next(it))
        if '{' in line:
            deep += 1
        if '}' in line:
            deep -= 1
            isVariable = False
            isTitle = False
        tokens = line.split('=')
        if len(tokens) == 2:
            if deep == 2 :
                scope = tokens[0]
                if isCharacter :
                    # Save previous character
                    if oneChar != None:
                        charStats.append(oneChar)
                    # Prepare to store the next one
                    oneChar = dict.fromkeys(list({scopeType}))
                    oneChar[scopeType] = scope
            
            # Variable parsing
            if isVariable:
                var.append({scopeType:scope, "variable":tokens[0],
                            "value":tokens[1]})
            if (deep == 3) & (variableKey in line):
                isVariable = True
              
            # Modifiers parsing
            if (tokens[0] == modifierToken) & (tokens[1] != '') & goodScopeModifier(deep, scopeType) :
                mod.append({scopeType:scope, "modifier":tokens[1]})
            
            # Title parsing
            if isProvince & (deep == 3) & (tokens[0].startswith("b_")) :
                title = tokens[0]
                isTitle = True             
            if isTitle & (tokens[0] == "type"):
                titTyp.append({provinceScope:scope, titleScope:title,
                               "type": tokens[1]})
                               
            # Character parsing
            if isCharacter & (tokens[0] in extractedCharStats):
                oneChar[charStatLib[tokens[0]]] = tokens[1]
    return (var, mod, it, i, titTyp, charStats)

#%%

def parse(lines):
    """
    Parse the lines of a CK2 savegame file
    
    :return: (provVar, provMod, titleVar, titTyp, charStats)
    """
    characterFound = False
    provinceFound = False
    titleFound = False
    n = len(lines)
    i = 0
    it = iter(lines)
    while (not titleFound) & (i < n):
        i += 1
        line = next(it)
        
        if characterKey in line:
           characterFound = True 
           while ((not '{' in line) & (i < n)):
                i += 1
                line = next(it)
           (charVar, charMod, it, i, empty, charStats) = parseScope(it, i, n, charScope)
        
        if characterFound & (provinceKey in line):
            provinceFound = True
            while ((not '{' in line) & (i < n)):
                i += 1
                line = next(it)
            (provVar, provMod, it, i, titTyp, empty) = parseScope(it, i, n, provinceScope)
            
        if provinceFound & (titleKey in line):
            titleFound = True
            while ((not '{' in line) & (i < n)):
                i += 1
                line = next(it)
            (titleVar, titleMod, it, i, empty, empty) = parseScope(it, i, n, titleScope)
    return (provVar, provMod, titleVar, titTyp, charStats)

#%%

def getYearFromFileName(fileName):
    parts = fileName.split('.')
    if len(parts) > 1:
        name = parts[0]
        parts = name.split('_')
        return parts[len(parts) - 1]
    return None
    
#%%
def createOrConcatDataFrame(dictionnary, df, year):
    """
    Create a dataframe or concatenate with df from a dictionnary
    
    :param dictionnary:
    :param df: if len(df) == 0 then create the dataframe,
                otherwise concatenate the dictionnary to df
    :param year: Added year information to the dictionnary
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
dfCharStats = pd.DataFrame()
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
    (provVar, provMod, titleVar, titleTyp, charStats) = parse(lines)
    
    # Data consolidation
    dfProvVar = createOrConcatDataFrame(provVar, dfProvVar, year)
    dfProvMod = createOrConcatDataFrame(provMod, dfProvMod, year)
    dfTitleVar = createOrConcatDataFrame(titleVar, dfTitleVar, year)
    dfCharStats = createOrConcatDataFrame(charStats, dfCharStats, year)
    
    
    # We only need the last values because it does not change
    # In fact some tribal titles can become castle, city or temple
    # We can do better by indicating the changing year
    dfTitleTyp = pd.DataFrame(titleTyp)
  
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
dfTitleTyp.to_csv(targetDir + "TitleTypes.csv", index=False)
dfCharStats.to_csv(targetDir + "CharacterStats.csv", index=False, encoding='utf-8')

