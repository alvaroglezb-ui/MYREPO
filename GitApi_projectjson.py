import requests
import json
import os
import pandas as pd
import openpyxl

# Configuración API de GitLab
GITLAB_URL = "https://fuentes.juntadeandalucia.es/api/v4"
PRIVATE_TOKEN = ""  # Reemplázalo con tu token

# ID directo de AUTOMATISMOS
AUTOMATISMOS_GROUP_ID = 645  # ID obtenido previamente

# Cabecera para autenticación
HEADERS = {
    "Private-Token": PRIVATE_TOKEN,
    "all_available":"true"}

def get_groups():
    """Obtiene todos los grupos accesibles y sus IDs"""
    url = f"{GITLAB_URL}/groups"
    params={
        "per_page":100
    }
    response = requests.get(url, headers=HEADERS,params=params)
    
    if response.status_code == 200:
        groups = response.json()
        print("\nGrupos disponibles:")
        for group in groups:
            print(f"Nombre: {group['name']}, ID: {group['id']}")
        return groups
    else:
        print(f"Error al obtener grupos: {response.status_code}")
        return None

def get_projects_in_group(group_id):
    """Obtiene todos los proyectos de un grupo específico"""
    url = f"{GITLAB_URL}/groups/{group_id}/projects"
    params={
        "per_page":300
    }
    response = requests.get(url, headers=HEADERS,params=params)
    
    if response.status_code == 200:
        projects = response.json()
        print(f"\nProyectos en el grupo {group_id}:")
        for project in projects:
            print(f"Nombre: {project['name']}, ID: {project['id']}")
            pass
        return projects
    else:
        print(f"Error al obtener proyectos: {response.status_code}")
        return None

def get_specific_group_id(path):
    """Obtiene el ID de un grupo específico basado en su path completo"""
    # Codifica el path para la URL
    encoded_path = requests.utils.quote(path, safe='')
    params={
        "per_page":100
    }
    url = f"{GITLAB_URL}/groups/{encoded_path}"
    response = requests.get(url, headers=HEADERS,params=params)
    
    if response.status_code == 200:
        group_info = response.json()
        return group_info['id']
    else:
        print(f"Error al obtener el grupo {path}: {response.status_code}")
        return None

def get_subgroups(group_id):
    """Obtiene todos los subgrupos de un grupo específico"""
    url = f"{GITLAB_URL}/groups/{group_id}/subgroups"
    params={
        "per_page":100
    }
    response = requests.get(url, headers=HEADERS,params=params)
    
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Error al obtener subgrupos: {response.status_code}")
        return None

def get_project_json_from_develop(project_id):
    """Obtiene el contenido del project.json de las ramas Develop y develop de un proyecto y sus subcarpetas"""
    def get_tree(project_id, path='', branch='develop'):
        url = f"{GITLAB_URL}/projects/{project_id}/repository/tree"
        all_items = []
        page = 1
        per_page = 100
        
        params = {
            "ref": branch, 
            "path": path,
            "per_page": per_page,
            "page": page
        }
        response = requests.get(url, headers=HEADERS, params=params)
        return response.json() if response.status_code == 200 else []

    def check_json_in_path(project_id, file_path, branch='develop'):
        encoded_path = requests.utils.quote(file_path, safe='')
        url = f"{GITLAB_URL}/projects/{project_id}/repository/files/{encoded_path}/raw"
        params = {"ref": branch}
        response = requests.get(url, headers=HEADERS, params=params)
        if response.status_code == 200:
            try:
                return {'branch': branch, 'content': response.json()}
            except json.JSONDecodeError:
                return None
        return None

    found_jsons = []
    
    def explore_directory(path='', branch='develop'):
        items = get_tree(project_id, path, branch)
        # Filtrar directamente por name='project.json'
        project_jsons = [item for item in items if item['name'] == 'project.json']
        
        for item in project_jsons:
            current_path = f"{path}/{item['name']}" if path else item['name']
            print(f"✓ Encontrado project.json en: {current_path} (rama: {branch})")
            json_content = check_json_in_path(project_id, current_path, branch)
            if json_content:
                found_jsons.append({
                    'path': current_path,
                    'branch': json_content['branch'],
                    'content': json_content['content']
                })
        
        # Explorar subdirectorios
        directories = [item for item in items if item['type'] == 'tree']
        for directory in directories:
            current_path = f"{path}/{directory['name']}" if path else directory['name']
            explore_directory(current_path, branch)

    # Explorar en ambas ramas
    explore_directory(branch='develop')
    explore_directory(branch='Develop')
    
    if not found_jsons:
        print("✗ No se encontró ningún project.json en este repositorio")
    
    return found_jsons if found_jsons else None

def explore_group_recursively(group_id, indent="", results=[]):
    """Explora recursivamente un grupo buscando archivos project.json"""
    projects = get_projects_in_group(group_id)
    if projects:
        print(f"\n{indent}Buscando project.json en los proyectos:")
        for project in projects:
            print(f"\n{indent}Proyecto: {project['name']}")
            project_jsons = get_project_json_from_develop(project['id'])
            if project_jsons:
                print(f"{indent}✓ project.json encontrado(s):")
                for json_file in project_jsons:
                    print(f"{indent}Ruta: {json_file['path']}")
                    print(f"{indent}Rama: {json_file['branch']}")
                    
                    if 'dependencies' in json_file['content']:
                        dependencies = json_file['content']['dependencies']
                        #excel_version = dependencies.get('UiPath.Excel.Activities', 'No encontrado')
                        #word_version = dependencies.get('UiPath.Word.Activities', 'No encontrado')
                        ada_ftp=dependencies.get('ADA.FTP', 'No encontrado')
                        # Buscar dependencias con "ADA"
                        ada_dependencies = {k: v for k, v in dependencies.items() if 'ADA' in k}
                        
                        results.append({
                            'Proyecto': project['name'],
                            'Ruta': json_file['path'],
                            #'Excel Activities': excel_version,
                            #'Word Activities': word_version,
                            'ADA.FTP':ada_ftp,
                            'ADA Dependencies': ada_dependencies
                        })
                        
                        if ada_dependencies:
                            print(f"{indent}✓ Dependencias ADA encontradas:")
                            for dep_name, dep_version in ada_dependencies.items():
                                print(f"{indent}  - {dep_name}: {dep_version}")
                        else:
                            print(f"{indent}✗ No se encontraron dependencias ADA")
                    else:
                        print(f"{indent}No se encontraron dependencies en este archivo")
                    
                    '''results.append({
                        'Proyecto': project['name'],
                        'Ruta': json_file['path']
                    })'''
            else:
                print(f"{indent}✗ No se encontró ningún project.json")

    # Obtener y explorar subgrupos
    subgroups = get_subgroups(group_id)
    if subgroups:
        for subgroup in subgroups:
            print(f"\n{indent}=== Subgrupo: {subgroup['name']} ===")
            explore_group_recursively(subgroup['id'], indent + "  ", results)

def print_all_projects_in_paths():
    """Imprime los project.json de las rutas específicas y sus subgrupos y guarda resultados en Excel"""
    paths = [
        "si-automatizacion-inteligente/automatismos/procesos-no-aloe"
    ]
    
    results = []
    for path in paths:
        print(f"\n\n=== Explorando {path} ===")
        group_id = get_specific_group_id(path)
        if group_id:
            explore_group_recursively(group_id, results=results)
    
    # Crear DataFrame y guardar en Excel
    if results:
        df = pd.DataFrame(results)
        df.to_excel('dependencias_uipath.xlsx', index=False)
        print("\nResultados guardados en 'dependencias_uipath.xlsx'")


def get_latest_commit_main_for_group(group_id,rama):
    """
    Para un grupo dado (por ID), obtiene todos los proyectos y muestra el último commit de la rama Main de cada uno.
    """
    projects = get_projects_in_group(group_id)
    if not projects:
        print(f"No se encontraron proyectos en el grupo {group_id}")
        return

    results=[]
    for project in projects:
        project_id = project['id']
        project_name = project['name']
        url_commits = f"{GITLAB_URL}/projects/{project_id}/repository/commits"
        params = {
            "ref_name": rama,
            "per_page": 200
        }
        response = requests.get(url_commits, headers=HEADERS, params=params)
        if response.status_code == 200:
            commits = response.json()
            if commits:
                commit = commits[0]
                print(f"Proyecto: {project_name}")
                print(f"  Último commit en Main: {commit['title']}- {commit['committer_name']} - ({commit['committed_date']})")
                results.append({
                    'Proyecto': project_name,
                    'Último commit en Main': commit['title'],
                    'Autor': commit['committer_name'],
                    'Fecha': commit['committed_date']
                })
            else:
                print(f"Proyecto: {project_name}")
                print("  No hay commits en la rama Main.")
        else:
            print(f"Proyecto: {project_name}")
            print(f"  Error al obtener commits: {response.status_code}")

    # Crear DataFrame y guardar en Excel
    if results:
        df = pd.DataFrame(results)
        df.to_excel(f'ultimos_commits_{rama}.xlsx', index=False)
        print("\nResultados guardados en 'ultimos_commits.xlsx'")

# Ejemplo de uso
if __name__ == "__main__":
    #print_all_projects_in_paths()
    get_latest_commit_main_for_group("5082","main")
