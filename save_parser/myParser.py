# -*- coding: utf-8 -*-
"""
Created on June 2017

@author: Nicolas
"""

import os
import io
import pandas as pd
import time

#%%  

saveDir = "../save_archiver/saves/"
targetDir = "../save_parser/results/"

#%%

savePrefix = "save_test_"

#%%

extractedCharStats = list({"b_d", "d_d", "prs", "piety", "wealth", "emp",
                           "host", "emi", "eyi", "rel", "cul", "bn", "fat", "mot"})
charStatLib = {"b_d" : "Birth date", "d_d" : "Death date", "prs" :"Prestige",
               "piety": "Piety", "wealth" : "Wealth", "emp" : "Employer",
               "host" : "Host", "emi" : "Estimated month income",
               "eyi" : "Estimated year income", "rel" : "Religion",
               "cul" : "Culture", "bn" : "Birth Name", "fat" : "Father",
               "mot": "Mother"}
               
extractedArtStats = list({"type", "owner", "org_owner", "obtained", "equipped",
                          "active"})
artColumnOrder = ["type", "owner", "org_owner", "obtained", "equipped",
                  "active", "year"]

#%%
provinceKey = "provinces="
variableKey = "variables="
titleKey = "title="
characterKey = "character="
artifactKey = "artifacts="

modifierToken = "modifier"
flagToken = "flags"

provinceScope = "province"
titleScope = "title"
charScope = "character"
artScope = "artifact"
artColumnOrder.insert(0, artScope)

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
    # No modifier in other scopes, so it is false
    return False;
            

#%%

def parseScope(it, init, n, scopeType):
    """
    Parse the scopes of a CK2 save game
    
    :param it: iterator of the lines when we are at the province key
    :param init: current line number
    :param n: number of lines in the file
    :param scopeType: name of the scope type
    :return: list of scope variables, modified it and init
    :rtype: (variable dictionnary, modifier dictionnary, iterator, int,
             title type dictionnary, character stats, flag dictionnary,
             artifact stats)
    """
    var = list()
    mod = list()
    flag = list()
    titTyp = list()
    charSt = list()
    artSt = list()
    i = init
    isProvince = (scopeType == provinceScope)
    isCharacter = (scopeType == charScope)
    isArt = (scopeType == artScope)

    deep = 2 # deep 0 = root, 1 = provinces
    isVariable = False # Is currently parsing a variable bloc
    isTitle = False # Is currently parsing a title bloc
    isFlag = False # Is currently parsing a flag bloc
    oneChar = None # Stats of one character
    oneArt = None # Stats of one artifact
    while (deep > 1) & (i < n):
        i += 1
        line = unspaced(next(it))
        if '{' in line:
            deep += 1
        if '}' in line:
            deep -= 1
            isVariable = False
            isTitle = False
            isFlag = False
        tokens = line.split('=')
        if len(tokens) == 2:
            if deep == 2 :
                scope = tokens[0]
                if isCharacter :
                    # Save previous character
                    if oneChar != None:
                        charSt.append(oneChar)
                    # Prepare to store the next one
                    oneChar = dict.fromkeys(list({scopeType}))
                    oneChar[scopeType] = scope
                if isArt :
                    # Save previous artifact
                    if oneArt != None:
                        artSt.append(oneArt)
                    # Prepare to store the next one
                    oneArt = dict.fromkeys(list({scopeType}))
                    oneArt[scopeType] = scope
            
            # Variable parsing
            if isVariable:
                var.append({scopeType:scope, "variable":tokens[0],
                            "value":tokens[1]})
            if (deep == 3) & (variableKey in line):
                isVariable = True
              
            # Modifiers parsing
            if (tokens[0] == modifierToken) & (tokens[1] != '') & goodScopeModifier(deep, scopeType) :
                mod.append({scopeType:scope, "modifier":tokens[1]})
                
            # Flag parsing
            if isFlag:
                flag.append({scopeType:scope, "flag":tokens[0], "date":tokens[1]})
            if (tokens[0] == flagToken) & (tokens[1] == ''):
                isFlag = True
            
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
                
            # Artifact parsing
            if isArt & (tokens[0] in extractedArtStats):
                oneArt[tokens[0]] = tokens[1]
    return (var, mod, it, i, titTyp, charSt, flag, artSt)

#%%

def parse(lines):
    """
    Parse the lines of a CK2 savegame file
    
    :return: (provVar, provMod, provFlag, titleVar, titleFlag, titTyp,
              charStats, charFlag, artFlag, artStats)
    """
    characterFound = False
    provinceFound = False
    titleFound = False
    artifactFound = False
    n = len(lines)
    i = 0
    it = iter(lines)
    while (not artifactFound) & (i < n):
        i += 1
        line = next(it)
        
        if (characterKey in line) & (not characterFound):
           characterFound = True 
           while ((not '{' in line) & (i < n)):
                i += 1
                line = next(it)
           (charVar, charMod, it, i, empty, charStats, charFlag, empty) = parseScope(it, i, n, charScope)
        
        if characterFound & (provinceKey in line) & (not provinceFound):
            provinceFound = True
            while ((not '{' in line) & (i < n)):
                i += 1
                line = next(it)
            (provVar, provMod, it, i, titTyp, empty, provFlag, empty) = parseScope(it, i, n, provinceScope)
            
        if provinceFound & (titleKey in line) & (not titleFound):
            titleFound = True
            while ((not '{' in line) & (i < n)):
                i += 1
                line = next(it)
            (titleVar, titleMod, it, i, empty, empty, titleFlag, empty) = parseScope(it, i, n, titleScope)
        
        if titleFound & (artifactKey in line) & (not artifactFound):
            artifactFound = True
            while ((not '{' in line) & (i < n)):
                i += 1
                line = next(it)
            (empty, empty, it, i, empty, empty, artFlag, artStats) = parseScope(it, i, n, artScope)
            
    return (provVar, provMod, provFlag, titleVar, titleFlag, titTyp, charStats,
            charFlag, artFlag, artStats)

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
def saveData(df, year, fileName, firstFileSaving=True):
    if (firstFileSaving):
        df.to_csv(fileName, index=False, encoding='utf-8')
    else:
        df.to_csv(fileName, mode='a', header=None, index=False, encoding='utf-8')

#%%

def computeExecutionTime(startTime):
    execTime = time.time() - startTime
    execTimeHour = int(execTime/3600)
    execTimeMin = int((execTime - execTimeHour*3600)/60)
    execTimeSec = int((execTime - execTimeHour*3600 - execTimeMin*60)*100)/100
    print('---- Done in {h} hours {m} minutes {s} seconds ---'.format(h=execTimeHour, m=execTimeMin, s=execTimeSec))

#%%

filesToParse = []
for fileName in os.listdir(saveDir):
    if fileName.startswith(savePrefix):
        filesToParse.append(fileName)
print("{} files to parse".format(len(filesToParse)))

#%%

startTime = time.time() 

firstFileSaving = True
dfArtFlag = pd.DataFrame()
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
    (provVar, provMod, provFlag, titleVar, titleFlag, titleTyp,
     charStats, charFlag, artFlag, artStats) = parse(lines)
     
    # Data consolidation
    dfProvVar = pd.DataFrame(provVar)
    dfProvVar["year"] = year
    dfProvMod = pd.DataFrame(provMod)
    dfProvMod["year"] = year
    dfProvFlag = pd.DataFrame(provFlag)
    dfProvFlag["year"] = year
    dfTitleVar = pd.DataFrame(titleVar)
    dfTitleVar["year"] = year
    dfTitleFlag = pd.DataFrame(titleFlag)
    dfTitleFlag["year"] = year
    dfCharStats = pd.DataFrame(charStats)
    dfCharStats["year"] = year
    dfCharFlag = pd.DataFrame(charFlag)
    dfCharFlag["year"] = year
    dfArtStats = pd.DataFrame(artStats)
    dfArtStats["year"] = year
    
    dfArtFlag = pd.concat([dfArtFlag, pd.DataFrame(artFlag)]).drop_duplicates()
     
    # Column ordering
    dfProvMod = dfProvMod[[provinceScope, "modifier", "year"]]
    dfProvFlag = dfProvFlag[[provinceScope, "flag", "date", "year"]]
    dfTitleFlag = dfTitleFlag[[titleScope, "flag", "date", "year"]]
    dfCharFlag = dfCharFlag[[charScope, "flag", "date", "year"]]
    dfArtStats = dfArtStats[artColumnOrder]
    
    saveData(dfProvVar, year, targetDir + savePrefix + "ProvinceVariables.csv",
             firstFileSaving)
    saveData(dfProvMod, year, targetDir + savePrefix + "ProvinceModifiers.csv",
             firstFileSaving)
    saveData(dfProvFlag, year, targetDir + savePrefix + "ProvinceFlags.csv",
             firstFileSaving)
    saveData(dfTitleVar, year, targetDir + savePrefix + "TitleVariables.csv",
             firstFileSaving)
    saveData(dfTitleFlag, year, targetDir + savePrefix + "TitleFlags.csv",
             firstFileSaving)
    saveData(dfCharStats, year, targetDir + savePrefix + "CharacterStats.csv",
             firstFileSaving)
    saveData(dfCharFlag, year, targetDir + savePrefix + "CharacterFlags.csv",
             firstFileSaving)
    saveData(dfArtStats, year, targetDir + savePrefix + "ArtifactStats.csv",
             firstFileSaving)
    firstFileSaving = False
    
    print("Year {} treated!".format(year))
    
computeExecutionTime(startTime)
    
#%%

# We only updated year by year
dfArtFlag = dfArtFlag[[artScope, "flag", "date"]]
dfArtFlag.to_csv(targetDir + savePrefix + "ArtifactFlags.csv", index=False)

# We only need the last values because they don't change
# In fact some tribal titles can become castle, city or temple
# We can do better by indicating the changing year
dfTitleTyp = pd.DataFrame(titleTyp)
dfTitleTyp.to_csv(targetDir + savePrefix + "TitleTypes.csv", index=False)   

