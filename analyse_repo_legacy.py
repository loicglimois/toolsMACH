import csv
import os
import yaml

import requests
import re
import xml.etree.ElementTree as ET
from collections import defaultdict

def count_files_with_extensions_hors(directory, extensions,hors):
    """
    Compte récursivement le nombre de fichiers avec des extensions spécifiques dans un répertoire.

    Args:
        directory (str): Le chemin du répertoire à analyser.
        extensions (tuple): Un tuple contenant les extensions à rechercher.

    Returns:
        int: Le nombre total de fichiers trouvés avec les extensions spécifiées.
    """
    file_count = 0

    print("      - count_files_with_extensions: ",extensions)

    # Parcourir tous les fichiers dans le répertoire et ses sous-répertoires
    for root, dirs, files in os.walk(directory):
        for file in files:
            file_path = os.path.join(root, file)
            # Vérifier si l'extension du fichier est dans la liste des extensions
            if file.endswith(extensions) and not hors in file_path:
                file_count += 1

    print("      - count_files_with_extensions:  nb: "+str(file_count))
    return file_count

def count_files_with_extensions(directory, extensions):
    """
    Compte récursivement le nombre de fichiers avec des extensions spécifiques dans un répertoire.

    Args:
        directory (str): Le chemin du répertoire à analyser.
        extensions (tuple): Un tuple contenant les extensions à rechercher.

    Returns:
        int: Le nombre total de fichiers trouvés avec les extensions spécifiées.
    """
    file_count = 0

    print("      - count_files_with_extensions: ",extensions)

    # Parcourir tous les fichiers dans le répertoire et ses sous-répertoires
    for root, dirs, files in os.walk(directory):
        for file in files:
            # Vérifier si l'extension du fichier est dans la liste des extensions
            if file.endswith(extensions):
                file_count += 1

    print("      - count_files_with_extensions:  nb: "+str(file_count))
    return file_count

def count_jsp_occurrences_in_faces_config(directory):
    """
    Recherche récursivement un fichier faces-config.xml dans un répertoire donné
    et compte le nombre d'occurrences de la chaîne '.jsp' dans ce fichier.

    Args:
        directory (str): Le chemin du répertoire à analyser.

    Returns:
        int: Le nombre d'occurrences de '.jsp' dans le fichier faces-config.xml.
    """
    jsp_count = 0
    faces_config_found = False

    print("      - jsp: recherche des .jsp dans fichier faces-config.xml")

    # Parcourir tous les fichiers dans le répertoire
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file == 'faces-config.xml':
                faces_config_found = True
                file_path = os.path.join(root, file)
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                        # Compter les occurrences de '.jsp'
                        jsp_count += content.count('.jsp')
                except Exception as e:
                    print(f"Erreur lors de la lecture du fichier {file_path}: {e}")

    if not faces_config_found:
        print("Aucun fichier faces-config.xml trouvé dans le répertoire spécifié.")

    print("        jps trouve:"+str(jsp_count))
    return jsp_count


def count_screen_jsf(base_dir):
    """
    Compte les fichiers .xhtml dans une application JSF.
    
    :param base_dir: Répertoire racine de l'application JSF.
    :return: Nombre total de fichiers .xhtml trouvés.
    """
    print("      - jsp: recherche des fichier .xhtml")

    total_ecrans = 0
    for root, _, files in os.walk(base_dir):
        for file in files:
            if file.endswith('.xhtml'):
                total_ecrans += 1
    
    print("          - nb ihm: .xhtml: "+str(total_ecrans))
    return total_ecrans


def get_jenkinsfile_deployer(directory, filename="Jenkinsfile"):
    """
    Lit un fichier Jenkinsfile et extrait la valeur de la variable 'deployer'.

    Args:
    directory (str): Chemin du répertoire contenant le Jenkinsfile.
    filename (str): Nom du fichier Jenkinsfile (par défaut "Jenkinsfile").

    Returns:
    tuple: (bool, str) - (True si trouvé, valeur de 'deployer') ou (False, None) si non trouvé.
    """
    file_path = os.path.join(directory, filename)
    
    if not os.path.exists(file_path):
        print(f"Le fichier {filename} n'existe pas dans le répertoire spécifié.")
        return False, None

    try:
        with open(file_path, 'r') as file:
            content = file.read()
            
            # Recherche de la variable 'deployer' avec une expression régulière
            match = re.search(r"deployer\s*:\s*'([^']*)'", content)
            
            if match:
                deployer_value = match.group(1)
                return True, deployer_value
            else:
                print("Variable 'deployer' non trouvée dans le fichier.")
                return False, None
    
    except Exception as e:
        print(f"Erreur lors de la lecture du fichier : {e}")
        return False, None


def detect_encoding_with_bom(file_path):
    """
    Détecte l'encodage d'un fichier en vérifiant le BOM et en ajoutant la détection pour ISO-8859 et ANSI.
    """
    with open(file_path, 'rb') as file:
        raw_data = file.read(4)  # Lire les 4 premiers octets
        if raw_data.startswith(b'\xef\xbb\xbf'):
            # print(" detect_encoding_with_bom: utf8")
            return 'utf-8-sig'
        elif raw_data.startswith(b'\xff\xfe'):
            # print(" detect_encoding_with_bom: utf16-le")
            return 'utf-16-le'
        elif raw_data.startswith(b'\xfe\xff'):
            # print(" detect_encoding_with_bom: utf16-be")
            return 'utf-16-be'
        elif raw_data.startswith(b'\xff\xfe\x00\x00'):
            # print(" detect_encoding_with_bom: utf32 le")
            return 'utf-32-le'
        elif raw_data.startswith(b'\x00\x00\xfe\xff'):
            # print(" detect_encoding_with_bom: utf32 be")
            return 'utf-32-be'
        else:
            # Vérification supplémentaire pour ISO-8859 et ANSI
            file.seek(0)  # Retourner au début du fichier
            content = file.read()
            try:
                content.decode('iso-8859-1')
                # print(" detect_encoding_with_bom: iso-8859")
                return 'iso-8859-1'
            except UnicodeDecodeError:
                try:
                    content.decode('cp1252')  # ANSI (Windows-1252)
                    # print(" detect_encoding_with_bom: ANSI")
                    return 'cp1252'
                except UnicodeDecodeError:
                    return 'unknown'


def count_screen_struts3(directory):
    """
    Compte le nombre d'IHM (interfaces utilisateur) dans une application Struts 2.
    
    Args:
        directory (str): Le chemin du répertoire à analyser.
    
    Returns:
        dict: Un dictionnaire contenant le nombre total d'IHM et la liste des JSP associées.
    """
    #action_pattern = r'<action\s+name="([^"]+)"\s+class="([^"]+)">'
    #action_pattern = r'<action\s+name="([^"]+)"'
    #result_pattern = r'<result\s+name="[^"]*">([^<]+)\.jsp</result>'
    result_pattern = r'<result>([^<]+)\.jsp</result>'

    #result_pattern = r'\.jsp</result>'
    #result_pattern = r'<result\s+name="[^"]*"'

    ihm_count = 0
    jsp_files = set()
    actions = defaultdict(list)

    print("      - comptage ecran Struts 2")

    # Parcourir tous les fichiers du répertoire
    for root, dirs, files in os.walk(directory):
        for file in files:
            if re.match(r'struts.*\.xml', file):  # Rechercher struts*.xml
                file_path = os.path.join(root, file)
                print("        - fichier a analyser:"+file_path)
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                    #with open(file_path, 'r', encoding=detect_encoding_with_bom(file_path) ) as f:
                        content = f.read()
                        print("         lecture fichier: ")

                        for result in re.finditer(result_pattern, content):
                            ihm_cur = result.group(1)
                            if( not ihm_cur in jsp_files):
                                jsp_files.add(ihm_cur)
                                ihm_count += 1

                except Exception as e:
                    print(f"Erreur lors de la lecture du fichier {file_path}: {e}")

    #ihm_count = len(jsp_files)
    print("              nb imh struts2: "+str(ihm_count))
    #return {"total_ihm": ihm_count, "jsp_files": list(jsp_files)}
    return ihm_count

def count_screen_struts1(directory):
    """Compter le nombre d'écrans dans une application Struts 1."""
    print("      - comptage ecran Struts 1")
    screen_count = 0
    # Expression régulière pour détecter les définitions d'écrans dans les fichiers JSP
    jsp_pattern = r'<jsp:include\s+page="([^"]+)"'
    # Expression régulière pour détecter les actions dans le fichier struts-config.xml
    action_pattern = r'<action\s+path="([^"]+)"'

    # Parcourir tous les fichiers dans le répertoire
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith('.jsp'):  # Considérer uniquement les fichiers JSP
                file_path = os.path.join(root, file)
                try:
                    with open(file_path, 'r', encoding=detect_encoding_with_bom(file_path) ) as f:
                        content = f.read()
                        # Compter les inclusions d'écrans dans le fichier JSP
                        screens_in_jsp = re.findall(jsp_pattern, content)
                        screen_count += len(screens_in_jsp)
                except UnicodeDecodeError:
                    # Si une erreur se produit lors de la lecture, ce n'est pas du UTF-8
                    print("        - "+file_path+" pas en utf8")

            elif re.match(r'struts-config-\w+\.xml', file):  # Vérifier le fichier de configuration Struts
                file_path = os.path.join(root, file)
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                        # Compter les actions qui représentent des écrans
                        actions_in_config = re.findall(action_pattern, content)
                        screen_count += len(actions_in_config)
                except UnicodeDecodeError:
                    # Si une erreur se produit lors de la lecture, ce n'est pas du UTF-8
                    print("        - "+file_path+" pas en utf8")

    print("        - ecran Struts 1: "+str(screen_count))
    return screen_count


def count_screen_gwt(directory):
    """Compter le nombre d'écrans GWT dans tous les fichiers Java d'un répertoire donné."""
    print("      -- compter_ecrans GWT "+directory)
    screen_count = 0
    screen_patterns = [
        # r'class\s+\w+\s+extends\s+(AbstractSuGwtPresenter)'
        r'@UiTemplate'
    ]

    # Parcourir tous les fichiers dans le répertoire
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith('.java'):  # Considérer uniquement les fichiers Java
                file_path = os.path.join(root, file)
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    # Vérifier chaque motif pour détecter les écrans
                    for pattern in screen_patterns:
                        if re.search(pattern, content):
                            screen_count += 1
                            break  # Compte chaque fichier une seule fois

    print("     nb ecran trouvé: "+str(screen_count))
    return screen_count

def count_screen_extjs(ext_js_directory):
    print("      -- compter_ecrans Ext.js "+ext_js_directory)

    screen_count = 0

    # screen_components = ['Ext.Panel', 'Ext.Viewport', 'Ext.Window', 'Ext.TabPanel']
    screen_components = ['Ext.Window']

    for root, dirs, files in os.walk(ext_js_directory):
        for file in files:
            if file.endswith('.js') or file.endswith('.jsp') :
                file_path = os.path.join(root, file)
                if (not "ext-" in file_path): 
                    #print(f"Analyzing file: {file_path}")

                    try:
                        with open(file_path, 'r', encoding='utf-8') as file:
                            for line in file:
                                for component in screen_components:
                                    if component in line:
                                        screen_count += 1  
                                # content = file.read()
                                # for component in screen_components:
                                #     if component in content:
                                #         screen_count += 1
                    except UnicodeDecodeError:
                        # Si une erreur se produit lors de la lecture, ce n'est pas du UTF-8
                        print("        - "+file_path+" pas en utf8")

    print("     nb ecran trouvé: "+str(screen_count))
    return screen_count

def rechercher_servlets_par_chaine(web_xml, chaine):
    nbSvt = 0;
    try:
        # Parse le fichier web.xml
        tree = ET.parse(web_xml)
        root = tree.getroot()

        # Espace de noms à utiliser pour l'analyse du XML
        namespaces = {'web': 'http://java.sun.com/xml/ns/javaee'}

        # Trouver tous les éléments <servlet>
        servlets = root.findall('web:servlet', namespaces)

        # Liste pour stocker les servlets dont la classe contient la chaîne
        servlets_trouves = []

        for servlet in servlets:
            # Trouver la balise <servlet-class>
            servlet_class = servlet.find('web:servlet-class', namespaces)
            if servlet_class is not None:
                # Vérifier si la chaîne de caractères recherchée est présente dans la servlet-class
                if chaine in servlet_class.text:
                    # Trouver le nom de la servlet
                    servlet_name = servlet.find('web:servlet-name', namespaces).text
                    servlets_trouves.append(servlet_name)
                    nbSvt += 1
        return nbSvt

    except ET.ParseError:
        print("Erreur lors de l'analyse du fichier XML.")
    except FileNotFoundError:
        print(f"Erreur : Le fichier {web_xml} n'a pas été trouvé.")
    except Exception as e:
        print(f"Une erreur s'est produite : {e}")
    
    return nbSvt



def get_group_id(repertoire):
    fic_pom = repertoire+"\\pom.xml"

    print("   -- recherche group id dans: "+fic_pom)
    try:
        # Parse le fichier XML
        tree = ET.parse(fic_pom)
        root = tree.getroot()

        # Recherche du groupId dans le fichier XML
        # Le groupId est normalement dans la balise <groupId>
        gi = root.find('{http://maven.apache.org/POM/4.0.0}groupId').text
        ai = root.find('{http://maven.apache.org/POM/4.0.0}artifactId').text
        if(gi and ai):
            print("  groupId:    "+gi)           
            print("  artifactId: "+ai)
            return [True,gi,ai]
        else:
            print("      * GroupId et artifactId non trouvé")
            return [False, None, None] # Si aucun groupId n'est trouvé
    except ET.ParseError:
        print("Erreur lors de l'analyse du fichier pom.XML.")
    except FileNotFoundError:
        print(f"Erreur : Le fichier pom.xml n'a pas eté trouve dans {repertoire}.")
    except Exception as e:
        print(f"Une erreur s'est produite : {e}")
    
    return [False, None, None]

def read_config_from_file(file_path ):
    config = {}
    try:
        with open(file_path, 'r') as file:
            for line in file:
                line = line.strip()  # Supprime les espaces et les retours à la ligne
                if ':' in line:
                    key, value = line.split(":", 1)  # Sépare la clé et la valeur
                    config[key] = value  # Ajoute à la hashmap (dictionnaire)
    except FileNotFoundError:
        print(f"Erreur : Le fichier {file_path} n'a pas été trouvé.")
    except Exception as e:
        print(f"Erreur lors de la lecture du fichier: {file_path} - {e}")
    
    return config


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

def search_webapp_in_arborescence( directory):
    print("  -- recherche webapp dans :"+ directory)
    chaine = "webapp"

    # On parcourt les répertoires et fichiers de manière récursive
    for root, dirs, files in os.walk(directory):
        # On cherche les répertoires dont le nom commence par "ext-"

        for curent in dirs:
            if curent == chaine :
                print(f"    * Trouvé dir deb: {os.path.join(root, curent)}")
                return [True,os.path.join(root, curent)]
    return [False,""]

#version_extjs = search_extjs( chemin_complet)
def search_extjs( chemin_complet):
    print("  -- recherche ext-  :"+ chemin_complet)

    pattern = r'ext-(\d+(\.\d+)*(\.\d+)?)'

    # On parcourt les répertoires et fichiers de manière récursive
    for root, dirs, files in os.walk(chemin_complet):
        # On cherche les répertoires dont le nom commence par "ext-"
        for curent in dirs:
            match = re.search(pattern, curent)
            if match:
                return "'"+match.group(1)+"'"
    return ""

def analyze_struts_version_v2(directory):
    """
    Recherche les chaînes "struts-config_1" et "struts-_2" dans tous les fichiers d'un répertoire donné.

    Args:
        directory (str): Le chemin du répertoire à analyser.

    Returns:
        dict: Un dictionnaire avec les chaînes recherchées comme clés et les fichiers correspondants comme valeurs.
    """
    # Chaînes à rechercher
    patterns = {
        "1": r'struts-config_1',
        "2": r'struts-2'
    }

    print("    - test struts")

    # Dictionnaire pour stocker les résultats
    #results = {key: [] for key in patterns.keys()}

    # Parcourir tous les fichiers dans le répertoire et ses sous-répertoires
    for root, dirs, files in os.walk(directory):
        for file in files:
            file_path = os.path.join(root, file)
            try:
                # Essayer d'ouvrir le fichier avec différents encodages
                for encoding in ['utf-8', 'iso-8859-1', 'cp1252']:
                    try:
                        with open(file_path, 'r', encoding=encoding) as f:
                            content = f.read()
                            # Vérifier chaque chaîne recherchée
                            for key, pattern in patterns.items():
                                if re.search(pattern, content):
                                    print("       - resultat: fichier config struts: "+file_path+ " V:"+key)
                                    return [True,key]
                                    # results[key].append(file_path)
                                    # break  # Sortir de la boucle des encodages si une correspondance est trouvée
                    except UnicodeDecodeError:
                        continue  # Essayer l'encodage suivant si celui-ci échoue
                    break  # Sortir de la boucle des encodages si la lecture réussit
            except Exception as e:
                print(f"Erreur lors de la lecture du fichier {file_path}: {e}")

#    return results
    return [False, "NA"]



def analyze_struts_version(directory):
    # struts1_pattern = r'http://struts\.apache\.org/dtds/struts-config_1[a-zA-Z0-9]+\.dtd'
    # struts2_pattern = r'http://struts\.apache\.org/dtds/struts-2[a-zA-Z0-9]+\.dtd'
    struts1_found = False
    struts2_found = False

    print("    - test struts")

    for root, dirs, files in os.walk(directory):
        for file in files:
            if re.match(r'struts.*\.xml', file):
                file_path = os.path.join(root, file)
                print("       - fichier config struts: "+file_path)

                try:
                    # with open(file_path, 'r', encoding=detect_encoding_with_bom(file_path)) as f:
                    with open(file_path, 'r') as f:
                        print("      - recherche des dtd")
                        # content = f.read()
                        # if re.search(struts1_pattern, content):
                        #     struts1_found = True
                        # if re.search(struts2_pattern, content):
                        #     istruts = True
                        #     struts2_found = True
                        # if struts1_found and struts2_found:
                        #     break
                        for line in f:
                            print("          line: "+line)
                            #if re.search(struts1_pattern, line):
                            if line.find("struts-config-1") != -1:
                                print("          line trouve: "+line)
                                struts1_found = True
                                break
                            if line.find("struts-2") != -1:
                                print("          line trouve: "+line)
                                struts2_found = True
                                break
                            if struts1_found and struts2_found:
                                break
                except UnicodeDecodeError:
                    print(f"le fichier n'est pas en utf8")
                except Exception as e:
                    print(f"Erreur lors de la lecture du fichier {file_path}: {e}")

    if struts1_found and not struts2_found:
        version = "1"
    elif struts2_found and not struts1_found:
        version = "2"
    elif struts1_found and struts2_found:
        version = "1 et 2"
    else:
        version = "N/A"
    
    print("      - version struts: "+ version )

    return [(struts1_found or struts1_found) ,version]

def search_text_in_arborescence(typeobj, chaine, directory, where ):
    
    print("  -- recherche "+typeobj+" - "+ chaine+" - "+ directory+" -"+where)
    
    if( typeobj == "dir" and directory.find(chaine) != -1 ):
        print(f"    * Trouvé "+chaine +" dans " + directory)
        return True
      
    # On parcourt les répertoires et fichiers de manière récursive
    for root, dirs, files in os.walk(directory):
        # On cherche les répertoires dont le nom commence par "ext-"

        if(typeobj == "dir"):
            for curent in dirs:
                # if re.match(rf'{re.escape(chaine)}', curent):
                #     print(f"    * Trouvé dir deb: {os.path.join(root, curent)}")
                #     return True
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
                # if re.match(rf'{re.escape(chaine)}', curent):
                #     print(f"    * Trouvé dir deb: {os.path.join(root, curent)}")
                #     return True

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

def get_lines_of_code(repo,group_id,artifact_id, url_sonar):
    nbloc = ""

    params = {
        "component": group_id+":"+artifact_id+":DEVELOP",
        "metricKeys": "ncloc"
    }
    # Effectuer la requête GET à l'API SonarQube
    response = requests.get(url_sonar, params=params, verify=False)

    # Si la réponse est correcte (code 200), traiter la réponse JSON
    if response.status_code == 200:
        data = response.json()
        try:
            # Extraire la valeur de 'ncloc' à partir de la réponse JSON
            nbloc = data["component"]["measures"][0]["value"]
            return nbloc
        except KeyError:
            print(f"Erreur: La métrique 'ncloc' n'a pas été trouvée pour le projet '{repo}'.")
            return nbloc
        except IndexError:
            print(f"Erreur: La métrique 'ncloc' n'a pas été trouvée pour le projet '{repo}'.")
            return nbloc
        finally:
            return nbloc
    else:
        print(f"Erreur lors de la requête pour le projet '{repo}': {response.status_code}")
        return nbloc

#Pour compter les API pour GWT
def count_methods_in_remote_service_classes(directory):
    """
    Recherche récursivement des fichiers .java dans un répertoire donné,
    vérifie si les classes étendent RemoteService et compte le nombre de méthodes.

    Args:
        directory (str): Le chemin du répertoire à analyser.

    Returns:
        int: Le nombre total de méthodes dans les classes qui étendent RemoteService.
    """
    total_methods = 0
    class_pattern = re.compile(r'interface\s+(\w+)\s+extends\s+RemoteService')
    #method_pattern = re.compile(r'\b(public|protected|private|static|final)?\s*\w+\s+\w+\s*\(.*\)\s*{')
    #method_pattern = re.compile(r'\w+\s+\w+\s*\(.*\)\s*;')
    #method_pattern = re.compile(r'\w+(?:<[^>]+>)?\s+\w+\s*\(.*?\)\s*;')
    method_pattern = re.compile(r'\b\w+(?:<[^>]+>)?\s+\w+\s*\(.*?\)\s*(?:throws\s+\w+(?:\s*,\s*\w+)*)?;')

    print("      - Cherche API GWT")

    # Parcourir tous les fichiers dans le répertoire et ses sous-répertoires
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith('.java'):
                file_path = os.path.join(root, file)
                #print("      - fichier Java: "+file_path)
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                        
                        # Vérifier si la classe étend RemoteService
                        if class_pattern.search(content):
                            # print("      - classe qui etend RemoteService: "+file_path)
                            # Compter les méthodes dans cette classe
                            methods = method_pattern.findall(content)
                            #print("        - nb methode"+str(len(methods)))
                            total_methods += len(methods)

                except Exception as e:
                    print(f"Erreur lors de la lecture du fichier {file_path}: {e}")

    print("      - nb methodes trouvées: "+str(total_methods))
    return total_methods


#Pour compter les API pour EXT.js  
def count_method_lines_in_dwr_xml(directory):
    """
    Recherche récursivement des fichiers nommés *.dwr.xml dans un répertoire donné
    et compte le nombre de lignes contenant 'methode="'.

    Args:
        directory (str): Le chemin du répertoire à analyser.

    Returns:
        int: Le nombre total de lignes contenant 'methode="' dans les fichiers .dwr.xml trouvés.
    """

    print("      - recherche method dans dwr.xml")
    total_count = 0

    # Parcourir tous les fichiers dans le répertoire et ses sous-répertoires
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith('dwr.xml') or file.endswith('ihm.xml') :
                file_path = os.path.join(root, file)
                try:
                    print("      - parcour du fichier "+file_path)
                    with open(file_path, 'r', encoding='utf-8') as f:
                        # Compter les lignes contenant 'methode="'
                        for line in f:
                            if 'method="' in line:
                                total_count += 1
                except Exception as e:
                    print(f"Erreur lors de la lecture du fichier {file_path}: {e}")

    return total_count


def rapportGenEntete(f):
    f.write("repo;exist;equipe;extjs;gwt;jsf;struts;jsp;ibmi;batch;lib;webapp;newsocle;archive;wso2;bdd;nbloc;nbsrvlt;nb_ecran_ext;version_extjs;nb_ecran_gwt;nb_ecran_jsf;nb_ecran_st;version_st;nb_jsp;deploiement\n")

#
def analyseWSO2(token, dir_repo,fic_result,mode,org_name,token_sonar, url_sonar):
    csv_filename = "D:\\workspace\\MACH2\\liste_wso2.csv"
    #fic_result   = "D:\\workspace\\MACH2\\inventaire_wso2.csv"
    repos = getRepoFromCSV(csv_filename)

    f = open(fic_result, mode)
    if(mode == "w"):
        rapportGenEntete(f)

    print("---------------------------------------------------------------------------------")
    print("analyseWSO2")
    print("---------------------------------------------------------------------------------")
    for repo in repos:
        chemin_complet = dir_repo + "\\" + repo
        print("- directory courant:" + repo+" - " +chemin_complet)

        team_cur  = ""
        dir_exist = False
        is_archive  = False
        type_bdd = "N/A"
        nbloc    = "NE"

        if os.path.isdir(chemin_complet):
            dir_exist = True

            team_cur = check_metadata_yaml(chemin_complet)
            is_archive = is_repo_archived(org_name, repo, token)

 
            if(dir_exist and not is_archive ):
                f.write(repo+";"+str(dir_exist)+";"+team_cur+";False;False;False;False;False;False;False;False;False;False;"+str(is_archive)+";True;"+type_bdd+";"+nbloc+";NE;NE;NE;NE;NE;NE;NE;NE;NE\n")
            print("    - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -  - - - - - - - - - - -")
        else:
            print(f"Repertoire non trouvé {chemin_complet}")

    f.close()

    return True



# Fonction principale
def analyseLegacy(token,dir_repo,fic_result,mode,org_name,token_sonar, url_sonar):
    # Nom du fichier CSV
    csv_filename = "D:\\workspace\\MACH2\\mach_tools\\liste_repo.csv"
    repos = getRepoFromCSV(csv_filename)

    #fic_result = "D:\\workspace\\MACH2\\liste_legacy.csv"
    chaine_recherchee = 'driverClassName="com.ibm.as400.access.AS400JDBCDriver"'

    f = open(fic_result, mode)
    rapportGenEntete(f)

    print("---------------------------------------------------------------------------------")
    print("analyse Java Legacy")
    print("liste repo: " + csv_filename)
    print("dir_repo: " + dir_repo)
    print("---------------------------------------------------------------------------------")

    for repo in repos:
        chemin_complet = dir_repo + "\\" + repo
        print("- directory courant:" + repo+" - " +chemin_complet)
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
        nbloc = ""
        nb_svt = 0
        nombre_ecrans_ext = 0
        nombre_ecrans_gwt = 0
        version_extjs = "N/A"
        nombre_ecrans_struts = 0
        version_struts = "N/A"
        nombre_ecran_jsf = 0
        nb_jsp           = 0
        deploiement = "NE"

        if os.path.isdir(chemin_complet):
            #print(f"Exploration du répertoire : {chemin_complet}")
            #Recherche EXT.JS
            team_cur = check_metadata_yaml(chemin_complet)
            #is_extjs = search_ext_subdirectories(chemin_complet)
            is_extjs     = search_text_in_arborescence("dir", "ext-", chemin_complet, "debut")
            if is_extjs:
                version_extjs = search_extjs( chemin_complet)
                nombre_ecrans_ext = count_screen_extjs(chemin_complet)
                if nombre_ecrans_ext == 0:
                    extensions = ('.jsp')
                    nombre_ecrans_ext = count_files_with_extensions_hors(chemin_complet, extensions, "ext-")

            is_gwt       = search_text_in_arborescence("file", ".gwt.xml", chemin_complet, "fin" )
            if is_gwt:
                nombre_ecrans_gwt = count_screen_gwt(chemin_complet)
            is_jsf       = search_text_in_arborescence("file", "faces-config.xml", chemin_complet, "debut")
            if is_jsf:
                nombre_ecran_jsf =  count_screen_jsf(chemin_complet)
                nombre_ecran_jsf += count_jsp_occurrences_in_faces_config(chemin_complet)

            test_struts = analyze_struts_version_v2(chemin_complet)
            is_struts      = test_struts[0]
            if is_struts:
                version_struts = test_struts[1]

                if test_struts[1] == "1":
                    nombre_ecrans_struts = count_screen_struts1(chemin_complet)
                elif test_struts[1] == "2":
                    nombre_ecrans_struts = count_screen_struts3(chemin_complet)


            #has_jsp      = search_text_in_arborescence("file", ".jsp", chemin_complet, "fin")
            
            if  not is_extjs and not is_gwt and  not is_jsf and  not is_struts:
                extensions = ('.jsp', '.html', '.htm')
                nb_jsp = count_files_with_extensions(chemin_complet, extensions)
                if nb_jsp > 0:
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
            is_batch = chercher_contenu_dans_nom(repo,"batch")
            is_lib   = chercher_contenu_dans_nom(repo,"agent")

            is_newsocle_1     = search_text_in_arborescence("dir", "-ms", chemin_complet, "fin")
            is_newsocle_2     = search_text_in_arborescence("dir", "-api", chemin_complet, "fin")
            is_newsocle = is_newsocle_1 or is_newsocle_2

            is_archive = is_repo_archived(org_name, repo, token)

            group_id = get_group_id(chemin_complet)
            if(group_id[0]):
                nbloc = get_lines_of_code(repo,group_id[1],group_id[2], url_sonar)

            webapp      = search_webapp_in_arborescence( chemin_complet)
            
            is_webapp = webapp[0]
            if is_webapp and group_id:
                # dirWebApp = webapp[1]
                # ficWebXml = dirWebApp+"\\WEB-INF\\web.xml"
                # nb_svt = rechercher_servlets_par_chaine(ficWebXml, group_id )
                nb_svt = 0
                if( is_extjs):
                    nb_svt += count_method_lines_in_dwr_xml(chemin_complet)
                if(is_gwt):
                    extensions = ('.jsp', '.html', '.htm')
                    nb_svt = count_methods_in_remote_service_classes(chemin_complet)

            get_deploiement = get_jenkinsfile_deployer(chemin_complet, "Jenkinsfile")
            if get_deploiement[0]:
                deploiement = get_deploiement[1]

        else:
            print(f"Le répertoire spécifié n'existe pas : {chemin_complet}")
            dir_exist = False
        
        if(dir_exist and not is_newsocle and not is_archive ):
            f.write(repo + ";" + str(dir_exist) + ";" + team_cur + ";" + str(is_extjs) + ";" + str(is_gwt) + ";" + str(is_jsf) + ";" + str(is_struts) + ";" + str(is_jsp) + ";" + str(is_ibmi) + ";" + str(is_batch) + ";" + str(is_lib) + ";" + str(is_webapp) + ";" + str(is_newsocle) + ";" + str(is_archive)+ ";False;" +type_bdd  + ";"+nbloc+";"+str(nb_svt)+";"+str(nombre_ecrans_ext)+";"+str(version_extjs)+";"+str(nombre_ecrans_gwt)+";"+str(nombre_ecran_jsf)+";"+str(nombre_ecrans_struts)+";"+str(version_struts)+";"+str(nb_jsp)+";"+deploiement+"\n")
        print("- - - - - - - - - - - - - - - - - - - - - - - - - - - - - -  - - - - - - - - - - -")

    f.close()

def menu():
    dir_repo = "D:\\workspace\\MACH2\\repo"
    org_name   = 'ugieiris'  # Remplacer par le nom de l'organisation
    #fic_result = "D:\\workspace\\MACH2\\resultat_analyse.csv"

    config  = read_config_from_file("..\\config.txt")  # Remplacer par votre token GitHub
    token_git   = config["git"]
    token_sonar = config["sonar"]

    url_sonar = "https://"+token_sonar+":@sonarqube.app.prod.gcp.groupement.systeme-u.fr/api/measures/component"

    print("Choisissez une action :")
    print("1. Analyse des repos Java Legacy")
    print("2. Analyse des repos WSO2")
    print("3. Analyse tous les types de repos")
    
    try:
        choice = int(input("Entrez le numéro de votre choix (1, 2 ou 3) : "))
         
        fic_result = "D:\\workspace\\MACH2\\resultat_inventaire_"+str(choice)+".csv"
   
        if choice == 1:
            analyseLegacy(token_git,dir_repo,fic_result,"w",org_name,token_sonar, url_sonar)
        elif choice == 2:
            analyseWSO2(token_git, dir_repo,fic_result,"w",org_name,token_sonar, url_sonar)
        elif choice == 3:
            analyseLegacy(token_git,dir_repo,fic_result,"w",org_name,token_sonar, url_sonar)  # Exécuter la fonction pour l'action 1
            analyseWSO2(token_git, dir_repo,fic_result,"a",org_name,token_sonar, url_sonar)
        else:
            print("Choix invalide. Veuillez entrer 1 ou 2.")
            menu()  # Redemander si le choix est invalide
    except ValueError:
        print("Veuillez entrer un numéro valide.")
        menu()  # Redemander en cas de saisie invalide


if __name__ == "__main__":
    menu()
