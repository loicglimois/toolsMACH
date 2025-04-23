@echo off
setlocal enabledelayedexpansion

REM Définir le répertoire de destination
set DEST_DIR=D:\workspace\MACH2\repo
set LST_REPO=D:\workspace\MACH2\liste_legacy.csv

rem set DEST_DIR=D:\workspace\MACH\gwt
rem set LST_REPO=D:\workspace\MACH\lst_gwt.csv

rem set DEST_DIR=D:\workspace\MACH\extjs
rem set LST_REPO=D:\workspace\MACH\liste_prj_ext.js.csv

REM https://github.com/ugieiris/AboDoc.git

set prefix_git=https://github.com/ugieiris/
set suffice_git=.git

echo Debut du clonage.
echo dir de clonage: %DEST_DIR%
echo liste : %LST_REPO%

REM Créer le répertoire si nécessaire
if not exist "%DEST_DIR%" (
    mkdir "%DEST_DIR%"
)

REM Aller dans le répertoire de destination
echo positionnement dans le repertoire cible: %DEST_DIR%

cd /d "%DEST_DIR%"

REM Lire le fichier ligne par ligne et cloner chaque dépôt
echo parcour du fichier: %LST_REPO%

for /f "tokens=*" %%a in (%LST_REPO%) do (
	set REPO_CUR=%prefix_git%%%a%suffice_git%
	echo Cloning repository: !REPO_CUR!
    git clone !REPO_CUR!
)

echo Tous les depots ont ete clones.
pause
