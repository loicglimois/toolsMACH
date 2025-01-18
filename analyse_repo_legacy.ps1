# Script PowerShell pour rechercher des répertoires "ext-*" et afficher le chemin du répertoire parent et le nom du répertoire trouvé

$path = "D:\workspace\MACH2\repo"  # Remplacez par le chemin où vous souhaitez commencer la recherche

#Equipe appartenance

#ExtJS
Get-ChildItem -Path $path -Recurse -Directory -Filter "ext-*" | ForEach-Object {
    $parentDir = $_.Parent.FullName   # Chemin du répertoire parent
    $parentDirName = $_.Parent.Name   # Nom du répertoire parent
    $dirName = $_.Name                # Nom du répertoire trouvé
    Write-Output "$parentDir;$parentDirName;$dirName"
}
