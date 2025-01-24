import requests

def get_org_repositories(org_name, token):
    url = f"https://api.github.com/orgs/{org_name}/repos"
    
    # Ajouter le token dans les en-têtes pour l'authentification
    headers = {
        'Authorization': f'Bearer {token}'
    }

    # Liste pour stocker les dépôts récupérés
    repos = []
    
    print("  -- requete initiale ")
    nbpage = 0
    # Effectuer la première requête pour récupérer les dépôts
    while url:
        response = requests.get(url, headers=headers)
        
        if response.status_code == 200:
            repos_data = response.json()
            nbpage += 1
            print("page courante: "+str(nbpage))
            for repo in repos_data:
                repos.append(repo['name'])  # Ajouter le nom de chaque dépôt à la liste
            
            # Vérifier s'il y a une page suivante
            if 'next' in response.links:
                url = response.links['next']['url']
            else:
                url = None  # Fin de la pagination
        else:
            print(f"Erreur lors de la récupération des dépôts: {response.status_code}")
            break

    print("page totale: "+str(nbpage))
    return repos

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

# Exemple d'utilisation
org_name   = 'ugieiris'  # Remplacer par le nom de l'organisation
token = read_token_from_file("..\\config.txt")  # Remplacer par votre token GitHub
if( token == None):
    exit(1)

fic_result = '..\\liste_repo_globale.csv'

print("recuperation de la liste complete des repo Git")
repos = get_org_repositories(org_name, token)

f = open(fic_result, "w")
f.write("repo;archive\n")

print("Affichage des resultats")
if repos:
    print(f"Dépôts de l'organisation {org_name}:")
    for repo in repos:
        is_archive = is_repo_archived(org_name,repo,token)
        f.write(repo+";"+str(is_archive)+"\n")
else:
    print("Aucun dépôt trouvé ou erreur.")

f.close()
