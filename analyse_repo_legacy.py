import csv
import os
import yaml

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

def search_text_in_arborescence(typeobj, chaine, directory,where ):
    
    print("  -- recherche "+typeobj+" - "+ chaine+" - "+ directory)
    
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

# Fonction principale
def main():
    # Nom du fichier CSV
    csv_filename = "D:\\workspace\\MACH2\\mach_tools\\liste_repo.csv"
    dir_repo = "D:\\workspace\\MACH2\\repo"
    fic_result = "D:\\workspace\\MACH2\\liste_legacy.csv"

    is_extjs = False
    is_gwt   = False
    is_jsf   = False
    is_extjs = False
    is_extjs = False
    is_jsp   = False
    is_ibmi  = False

    print("---------------------------------------------------------------------------------")
    print("Debut du programme")
    print("liste repo: " + csv_filename)
    print("dir_repo: " + dir_repo)
    print("---------------------------------------------------------------------------------")


    f = open(fic_result, "w")
    f.write("repo;equipe;extjs;gwt;jsf;struts;jsp;ibmi\n")
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
                        is_ibmi      = search_text_in_arborescence("file", ".suopcml", chemin_complet, "fin")
                            
                    else:
                        print(f"Le répertoire spécifié n'existe pas : {chemin_complet}")
                    
                    f.write(directory + ";" + team_cur + ";" + str(is_extjs) + ";" + str(is_gwt) + ";" + str(is_jsf) + ";" + str(is_struts) + ";" + str(is_jsp) + ";" + str(is_ibmi) + "\n")
                    print("- - - - - - - - - - - - - - - - - - - - - - - - - - - - - -  - - - - - - - - - - -")

    except FileNotFoundError:
        print(f"Erreur : Le fichier {csv_filename} n'a pas été trouvé.")
    except Exception as e:
        print(f"Une erreur s'est produite : {e}")
    f.close()


if __name__ == "__main__":
    main()
