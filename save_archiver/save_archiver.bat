:::::::::::::::::::
:: Save archiver ::
:::::::::::::::::::
:: This script copy the autosave.ck2 file in target directory.
:: The copy has a also its prefix defined by the target variable.
:: The name is completed by year and the .ck2 extension.

:: PARAMETEES
:: %1 : Modification type (CREATE, UPDATE or DELETE)
:: %2 : Modified file

:: Target directory and prefix
:: %~dp0 is the script directory
set "target=%~dp0%saves\save_test"

:: Variable to know if the save erase or not a previous file
:: - 0 : erases the old verion
:: - otherwise : keeps the old version and doesn't archive
set erase=0

:: Interest file
set interestFile=autosave.ck2

:: We are only intested by creation or updating
if %1 == "DELETE" ( exit )

:: Check that the changed file is the interest file
for %%A in (%2) do (set name=%%~nxA)
if NOT "%name%" == "%interestFile%" ( exit )
echo %date% %time% : %1 %2 >> "%~dp0%log.txt"

:: Get the in-game date
for /F "usebackq skip=2 delims=" %%i in (%2) do set "gamedate=%%i"&goto nextline
:nextline
echo %date% %time% : in-game date = %gamedate% >> "%~dp0%log.txt"

:: Get the year from the gamedate
:: 2nd part of =
for /F "tokens=2 delims==" %%A IN ("%gamedate%") DO (set gamedate=%%A)
:: 1st part of .
for /F "tokens=1 delims=." %%A IN ("%gamedate%") DO (set gamedate=%%A)
:: Remove double quote
set year=%gamedate:"=%
echo %date% %time% : in-game year = %year% >> "%~dp0%log.txt"

:: Add 0 before the year to have year in 4 characters
if %year% lss 10 set year=0%year%
if %year% lss 100 set year=0%year%
if %year% lss 1000 set year=0%year%

:: Copy the file
if %erase% == 0 (
	copy %2 "%target%_%year%.ck2"
	echo %date% %time% : %target%_%year%.ck2 archived >> "%~dp0%log.txt"
) else (
	if not exist "%target%_%year%.ck2" (
		copy %2 "%target%_%year%.ck2"
		echo %date% %time% : %target%_%year%.ck2 archived >> "%~dp0%log.txt"
	)
)
