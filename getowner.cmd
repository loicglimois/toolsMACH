@echo off
setlocal enabledelayedexpansion

REM Pourcours le fichier %LST_REPO%.csv
REM parcours les repertoires correspondant aux lignes du fichier
REM		Recupere le owner du repo GIT dans le fichier metadata.
REM appel API Git pour avoir date de modif
REM
REM sauvegarde dans un fichier csv du type:
REM PROJET;OWNER;nblignes

rem set LST_REPO=D:\workspace\MACH\liste_prj_ext.js.csv
rem set LST_REPO=D:\workspace\MACH\liste_prj_ext.js_all.csv
REM Définir le répertoire contenant les dépôts clonés
rem set REPOS_DIR=D:\workspace\MACH\extjs

rem set LST_REPO=D:\workspace\MACH\liste_prj_ext.js.csv
rem set LST_REPO=D:\workspace\MACH\lst_gwt.csv
REM Définir le répertoire contenant les dépôts clonés
rem set REPOS_DIR=D:\workspace\MACH\gwt

rem set LST_REPO=D:\workspace\MACH\liste_prj_ext.js.csv
set LST_REPO=D:\workspace\MACH\lst_ibmi.csv
REM Définir le répertoire contenant les dépôts clonés
set REPOS_DIR=D:\workspace\MACH\ibmi

REM Définir le fichier de sortie
set OUTPUT_FILE=owners_list.txt

set GIT_TOKEN=
set prefix_git=https://api.github.com/repos/ugieiris
set suffice_git=.git

REM Supprimer le fichier de sortie s'il existe déjà
if exist "%OUTPUT_FILE%" del "%OUTPUT_FILE%"

REM Lire le fichier ligne par ligne et cloner chaque dépôt
echo parcour du fichier: %LST_REPO%

REM Parcourir chaque sous-répertoire dans le répertoire des dépôts clonés
rem for /d %%a in ("%REPOS_DIR%\*") do (
for /f "tokens=*" %%a in (%LST_REPO%) do (
	set REPO_CUR=%REPOS_DIR%\%%a
	echo repo courant: %%a - dir complet: !REPO_CUR!
    REM Vérifier si le fichier metadata.yaml existe dans le dépôt
    if exist "!REPO_CUR!\.repo\metadata.yaml" (
        REM Chercher le champ "owners" dans le fichier metadata.yaml
        for /f "tokens=1,* delims=:" %%b in ('findstr /i "owners" "!REPO_CUR!\.repo\metadata.yaml"') do (
            REM Extraire le nom de l'équipe (en retirant les espaces et les guillemets)
            set TEAM_NAME=%%c
            set TEAM_NAME=!TEAM_NAME: =!
            set TEAM_NAME=!TEAM_NAME:"=!

            REM Écrire le nom du dépôt et le nom de l'équipe dans le fichier de sortie
            rem echo %%~nxa; !TEAM_NAME! >> "%OUTPUT_FILE%"
        )
    ) else (
		rem echo %%a\.repo\metadata.yaml
        REM Si le fichier metadata.yaml n'est pas trouvé, écrire une alerte
        echo Fichier \.repo\metadata.yaml non trouve dans le depot %%~nxa
		rem echo %%~nxa; "non trouve" >> "%OUTPUT_FILE%"
		set TEAM_NAME="non trouve"

    )

    set REPO_URL=%prefix_git%/%%a%/commits?per_page=1

    REM Utiliser wget pour appeler l'API et récupérer les informations JSON du dernier commit
    echo repo cur: !REPO_URL!
	curl -s "!REPO_URL!" -H "Authorization: Bearer %GIT_TOKEN%" -H "Accept: application/vnd.github+json" > response.json

    REM Extraire la date du dernier commit depuis le fichier JSON
    for /f "tokens=2 delims=:," %%b in ('findstr /i "date" response.json') do (
        set COMMIT_DATE=%%b
        REM Nettoyer les guillemets et les espaces
        set COMMIT_DATE=!COMMIT_DATE:"=!
        set COMMIT_DATE=!COMMIT_DATE: =!
    )
	
	echo %%~nxa;!TEAM_NAME!;!COMMIT_DATE! >> "%OUTPUT_FILE%"
)

echo Traitement terminé. Les résultats sont dans %OUTPUT_FILE%.
pause