import csv
import os
import yaml

import requests
import re

def read_token_from_file(file_path):
    try:
        with open(file_path, 'r') as file:
            token = file.read().strip()  # Enlever les espaces et les sauts de ligne
        return token
    except FileNotFoundError:
        print(f"Le fichier {file_path} n'a pas été trouvé.")
        return None
    except Exception as e:
        print(f"Erreur lors de la lecture du fichier: {file_path} - {e}")
        return None


def is_repo_archived(owner, repo, token):
    url = f"https://api.github.com/repos/{owner}/{repo}"
    
    print("    --- check if repo archived: "+ repo)

    # Ajouter le token dans les en-têtes pour l'authentification
    headers = {
        'Authorization': f'Bearer {token}'
    }
    
    response = requests.get(url, headers=headers)
    
    if response.status_code == 200:
        repo_data = response.json()
        return repo_data.get('archived', False)
    else:
        print(f"Erreur lors de la récupération des informations du dépôt: {response.status_code}")
        return False

def chercher_contenu_dans_fichier(fichier, chaine):
    """Vérifie si le fichier contient la chaîne spécifiée."""
    try:
        with open(fichier, 'r', encoding='utf-8') as f:
            contenu = f.read()
            return chaine in contenu
    except Exception as e:
        print(f"Erreur lors de l'ouverture du fichier {fichier}: {e}")
        return False


def rechercher_driver(fichier):
    # Expression régulière pour trouver la chaîne de type xxxx.DRIVER=yyyy
    #pattern = r'^(?!#)(\S+)\.DRIVER=(\S+)'
    pattern = r'^\s*(?!#)(\S+)\.DRIVER=(\S+)'

    with open(fichier, 'r') as file:
        # Lire toutes les lignes du fichier
        for line in file:
            # Recherche de la chaîne correspondant au pattern
            match = re.search(pattern, line)
            if match:
                # Affichage des résultats trouvés
                xxxx = match.group(1)
                yyyy = match.group(2)
                print(f"Trouvé : {xxxx}.DRIVER={yyyy}")
                return yyyy
    return "unknow"

#type_bdd = getTypeBdd(chemin_complet)
def getTypeBdd(dossier):
    """Recherche récursive de tous les fichiers context.xml dans un dossier et vérifie le contenu."""
    for root, dirs, files in os.walk(dossier):
        for file in files:
            if file == 'dbpools.properties':
                chemin_fichier = os.path.join(root, file)
                #Cherche fichier pour Batch
                type = rechercher_driver(chemin_fichier)
                if not type == "unknow":
                    return type

    return "unknow"

def rechercher_fichiers_context_xml(dossier, chaine):
    """Recherche récursive de tous les fichiers context.xml dans un dossier et vérifie le contenu."""
    for root, dirs, files in os.walk(dossier):
        for file in files:
            if file == 'context.xml':
                chemin_fichier = os.path.join(root, file)
                if chercher_contenu_dans_fichier(chemin_fichier, chaine):
                    print(f"Le fichier {chemin_fichier} contient la chaîne recherchée.")
                    return True
                else:
                    print(f"Le fichier {chemin_fichier} ne contient pas la chaîne recherchée.")
                    return False
    return False

def chercher_contenu_dans_nom(nom, chaine):
    if nom.find(chaine) != -1:
        print( "  --- "+nom + " contient: " + chaine )
        return True
    else:
        return False


# Fonction pour rechercher récursivement les sous-répertoires "ext-"
# return true si trouvé
# return false si trouvé
def search_ext_subdirectories(directory):
    # On parcourt les répertoires et fichiers de manière récursive
    for root, dirs, files in os.walk(directory):
        # On cherche les répertoires dont le nom commence par "ext-"
        for dir_name in dirs:
            if dir_name.startswith("ext-"):
                print(f"Trouvé : {os.path.join(root, dir_name)}")
                return True
    return False

def search_text_in_arborescence(typeobj, chaine, directory, where ):
    
    print("  -- recherche "+typeobj+" - "+ chaine+" - "+ directory+" ou "+where)
    
    if( typeobj == "dir" and directory.find(chaine) != -1 ):
        print(f"    * Trouvé "+chaine +" dans " + directory)
        return True
    #print("    -- debut recursif "+directory)
      
    # On parcourt les répertoires et fichiers de manière récursive
    for root, dirs, files in os.walk(directory):
        # On cherche les répertoires dont le nom commence par "ext-"

        if(typeobj == "dir"):
            for curent in dirs:
                if where == "debut":
                    if curent.find(chaine) != -1 :
                        print(f"    * Trouvé dir deb: {os.path.join(root, curent)}")
                        return True
                if where == "fin":
                    if curent.find(chaine) != -1 :
                        print(f"    * Trouvé dir end : {os.path.join(root, curent)}")
                        return True
        if(typeobj == "file"):
            for curent in files:
                if where == "debut":
                    if curent.find(chaine) != -1 :
                        print(f"    * Trouvé fic deb: {os.path.join(root, curent)}")
                        return True 
                if where == "fin":
                    if curent.find(chaine) != -1 :                        
                        print(f"    * Trouvé fic fin: {os.path.join(root, curent)}")
                        return True 
    return False



# Fonction pour rechercher et lire le fichier metadata.yaml
def check_metadata_yaml(directory):
    # Chemin du fichier metadata.yaml
    repo_dir = os.path.join(directory, ".repo")
    metadata_file = os.path.join(repo_dir, "metadata.yaml")
    
    team_cur = "VIDE"
    
    print("  -- recherche proprietaire "+metadata_file)
    # Vérifie si le fichier existe
    if os.path.exists(metadata_file):
        try:
            # Ouverture du fichier YAML
            with open(metadata_file, 'r') as file:
                data = yaml.safe_load(file)
                # Recherche du champ 'owners'
                if 'organization' in data and 'owners' in data['organization']:
                    team_cur = data['organization']['owners']
                    print(f"      Propriétaires dans {metadata_file} : {team_cur}")
                    return team_cur
                else:
                    print(f"      Champ 'owners' non trouvé dans {metadata_file}")
        except yaml.YAMLError as e:
            print(f"Erreur lors de la lecture de {metadata_file}: {e}")
        except Exception as e:
            print(f"Erreur inconnue : {e}")
    else:
        print(f"Le fichier {metadata_file} n'existe pas.")
    return team_cur

def getRepoFromCSV(csv_input):
    repos = []
    try:
        with open(csv_input, mode='r', newline='') as file:
            csv_reader = csv.reader(file)
            print("Parcours du CSV")
            
            for row in csv_reader:
                if row:  # On s'assure que la ligne n'est pas vide
                    directory = row[0].strip()
                    repos.append(directory) 
    except FileNotFoundError:
        print(f"Erreur : Le fichier {csv_input} n'a pas été trouvé.")
    except Exception as e:
        print(f"Une erreur s'est produite : {e}")

    return repos

def analyseWSO2(token, dir_repo):
    csv_filename = "D:\\workspace\\MACH2\\wso2_liste.csv"
    fic_result   = "D:\\workspace\\MACH2\\inventaire_wso2.csv"
    repos = getRepoFromCSV(csv_filename)

    f = open(fic_result, "w")
    f.write("repo;exist;equipe;extjs;gwt;jsf;struts;jsp;ibmi;batch;lib;webapp;newsocle;archive;wso2\n")

    print("---------------------------------------------------------------------------------")
    print("analyseWSO2")
    print("---------------------------------------------------------------------------------")
    for repo in repos:
        chemin_complet = dir_repo + "\\" + repo
        print("- directory courant:" + repo+" - " +chemin_complet)

        if os.path.isdir(chemin_complet):
            team_cur = check_metadata_yaml(chemin_complet)
            print("    "+repo+";True;"+team_cur+";False;False;False;False;False;False;False;False;False;False;False;True\n")
            f.write(repo+";True;"+team_cur+";False;False;False;False;False;False;False;False;False;False;False;True\n")
            print("    - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -  - - - - - - - - - - -")
        else:
            print(f"Repertoire non trouvé {chemin_complet}")

    f.close()

    return True

# Fonction principale
def analyseLegacy(token,dir_repo,org_name):
    # Nom du fichier CSV
    csv_filename = "D:\\workspace\\MACH2\\mach_tools\\liste_repo.csv"
  
    fic_result = "D:\\workspace\\MACH2\\liste_legacy.csv"
    chaine_recherchee = 'driverClassName="com.ibm.as400.access.AS400JDBCDriver"'

    # is_extjs  = False
    # is_gwt    = False
    # is_jsf    = False
    # is_extjs  = False
    # is_extjs  = False
    # is_jsp    = False
    # is_ibmi   = False
    # dir_exist = False
    # is_batch  = False

    print("---------------------------------------------------------------------------------")
    print("Debut du programme")
    print("liste repo: " + csv_filename)
    print("dir_repo: " + dir_repo)
    print("---------------------------------------------------------------------------------")


    f = open(fic_result, "w")
    f.write("repo;exist;equipe;extjs;gwt;jsf;struts;jsp;ibmi;batch;lib;webapp;newsocle;archive;wso2;bdd\n")

    # str(dir_exist) + ";" + team_cur + ";" + str(is_extjs) + ";" + str(is_gwt) + ";" + str(is_jsf) + ";" + str(is_struts) + ";" + str(is_jsp) + ";" 
    # + str(is_ibmi) + ";" + str(is_batch) + ";" + str(is_lib) + ";" + str(is_webapp) + ";" + str(is_newsocle) + "\n")
    # Lecture du fichier CSV contenant la liste des répertoires
    try:
        with open(csv_filename, mode='r', newline='') as file:
            csv_reader = csv.reader(file)
            print("Parcours du CSV")
            
            for row in csv_reader:
                if row:  # On s'assure que la ligne n'est pas vide
                    directory = row[0].strip()

                    chemin_complet = dir_repo + "\\" + directory
                    print("- directory courant:" + directory+" - " +chemin_complet)
                    #print("chemin complet :" + chemin_complet)

                    team_cur  = ""
                    is_extjs  = False
                    is_gwt    = False
                    is_jsf    = False
                    is_struts = False
                    is_extjs  = False
                    is_extjs  = False
                    is_jsp    = False
                    is_ibmi   = False
                    dir_exist = False
                    is_batch  = False
                    is_lib    = False
                    is_webapp = False
                    is_newsocle = False
                    is_archive  = False
                    type_bdd = ""

                    if os.path.isdir(chemin_complet):
                        #print(f"Exploration du répertoire : {chemin_complet}")
                        #Recherche EXT.JS
                        team_cur = check_metadata_yaml(chemin_complet)
                        #is_extjs = search_ext_subdirectories(chemin_complet)
                        is_extjs     = search_text_in_arborescence("dir", "ext-", chemin_complet, "debut")
                        is_gwt       = search_text_in_arborescence("file", ".gwt.xml", chemin_complet, "fin" )
                        is_jsf       = search_text_in_arborescence("file", "faces-config.xml", chemin_complet, "debut")
                        debut_struts = search_text_in_arborescence("file", "struts-", chemin_complet, "debut")
                        fin_struts   = search_text_in_arborescence("file", ".xml", chemin_complet, "fin")
                        is_struts    = debut_struts and fin_struts
                        has_jsp      = search_text_in_arborescence("file", ".jsp", chemin_complet, "fin")
                        if  not is_extjs and not is_gwt and  not is_jsf and  not is_struts and has_jsp :
                            is_jsp = True
                        else:
                            is_jsp = False
                        is_ibmi1      = search_text_in_arborescence("file", ".suopcml", chemin_complet, "fin")
                        is_ibmi2     = rechercher_fichiers_context_xml(chemin_complet, chaine_recherchee)
                        is_ibmi = is_ibmi1 or is_ibmi2
                        if not is_ibmi:
                            type_bdd = getTypeBdd(chemin_complet)
                        else:
                            type_bdd = "IBMi"
                        dir_exist = True
                        is_batch = chercher_contenu_dans_nom(directory,"batch")
                        is_lib   = chercher_contenu_dans_nom(directory,"agent")
                        is_webapp      = search_text_in_arborescence("dir", "webapp", chemin_complet, "fin")
                        is_newsocle_1     = search_text_in_arborescence("dir", "-ms", chemin_complet, "fin")
                        is_newsocle_2     = search_text_in_arborescence("dir", "-api", chemin_complet, "fin")
                        is_newsocle = is_newsocle_1 or is_newsocle_2

                        is_archive = is_repo_archived(org_name, directory, token)

                    else:
                        print(f"Le répertoire spécifié n'existe pas : {chemin_complet}")
                        dir_exist = False
                    
                    if(dir_exist and not is_newsocle and not is_archive ):
                        f.write(directory + ";" + str(dir_exist) + ";" + team_cur + ";" + str(is_extjs) + ";" + str(is_gwt) + ";" + str(is_jsf) + ";" + str(is_struts) + ";" + str(is_jsp) + ";" + str(is_ibmi) + ";" + str(is_batch) + ";" + str(is_lib) + ";" + str(is_webapp) + ";" + str(is_newsocle) + ";" + str(is_archive)+ ";False;" +type_bdd  + "\n")
                    print("- - - - - - - - - - - - - - - - - - - - - - - - - - - - - -  - - - - - - - - - - -")

    except FileNotFoundError:
        print(f"Erreur : Le fichier {csv_filename} n'a pas été trouvé.")
    except Exception as e:
        print(f"Une erreur s'est produite : {e}")
    f.close()

def menu():
    dir_repo = "D:\\workspace\\MACH2\\repo"
    org_name   = 'ugieiris'  # Remplacer par le nom de l'organisation
    token = read_token_from_file("..\\config.txt")  # Remplacer par votre token GitHub

    print("Choisissez une action :")
    print("1. Analyse des repos Java Legacy")
    print("2. Analyse des repos WSO2")
    
    try:
        choice = int(input("Entrez le numéro de votre choix (1 ou 2) : "))
        
        if choice == 1:
            analyseLegacy(token,dir_repo,org_name)  # Exécuter la fonction pour l'action 1
        elif choice == 2:
            analyseWSO2(token,dir_repo)  # Exécuter la fonction pour l'action 2
        else:
            print("Choix invalide. Veuillez entrer 1 ou 2.")
            menu()  # Redemander si le choix est invalide
    except ValueError:
        print("Veuillez entrer un numéro valide.")
        menu()  # Redemander en cas de saisie invalide


if __name__ == "__main__":
    menu()
