import requests
import json
import os
import pandas as pd

# Configuración API de GitLab
GITLAB_URL = "https://fuentes.juntadeandalucia.es/api/v4"
PRIVATE_TOKEN = "glpat-Y3NgGBAQtYUhM2YzjECD"  # Reemplázalo con tu token

# ID directo de AUTOMATISMOS
AUTOMATISMOS_GROUP_ID = 645  # ID obtenido previamente

# Cabecera para autenticación
HEADERS = {"Private-Token": PRIVATE_TOKEN}

# Función para obtener TODOS los subgrupos con paginación
def get_all_subgroups(group_id):
    subgroups = []
    page = 1
    while True:
        url = f"{GITLAB_URL}/groups/{group_id}/subgroups"
        response = requests.get(url, headers=HEADERS, params={"per_page": 100, "page": page})
        if response.status_code != 200:
            break
        data = response.json()
        if not data:
            break
        subgroups.extend(data)
        page += 1  # Pasar a la siguiente página
    return subgroups

# Función para obtener TODOS los proyectos con paginación
def get_all_projects(group_id):
    projects = []
    page = 1
    while True:
        url = f"{GITLAB_URL}/groups/{group_id}/projects"
        response = requests.get(url, headers=HEADERS, params={"per_page": 100, "page": page})
        if response.status_code != 200:
            break
        data = response.json()
        if not data:
            break
        projects.extend(data)
        page += 1  # Pasar a la siguiente página
    return projects

# Obtener subgrupos dentro de AUTOMATISMOS
subgroups_automatismos = get_all_subgroups(AUTOMATISMOS_GROUP_ID)

# Buscar el subgrupo PROCESOS NO ALOE
procesos_no_aloe_group = next((g for g in subgroups_automatismos if "PROCESOS NO ALOE" in g["name"].upper()), None)
if not procesos_no_aloe_group:
    print("🚨 No se encontró el subgrupo PROCESOS NO ALOE dentro de AUTOMATISMOS.")
    exit()

# Obtener todos los subgrupos dentro de PROCESOS NO ALOE (cada uno representa un proceso)
procesos = get_all_subgroups(procesos_no_aloe_group["id"])

# Verificar qué procesos se han detectado
print("\n🔹 Procesos detectados dentro de PROCESOS NO ALOE:")
for proceso in procesos:
    print(f"   - {proceso['name']} (ID: {proceso['id']}) - {proceso['full_path']}")

# Extraer repositorios de cada proceso
data = {
    "group_id": procesos_no_aloe_group["id"],
    "group_name": procesos_no_aloe_group["full_path"],
    "procesos": []
}

# Nueva función para obtener el contenido del project.json
def get_project_json_content(project_id):
    try:
        # Primero obtenemos el contenido codificado en base64
        url = f"{GITLAB_URL}/projects/{project_id}/repository/files/project.json/raw"
        response = requests.get(url, headers=HEADERS, params={"ref": "main"})
        
        if response.status_code == 200:
            try:
                # Intentamos parsear el JSON
                return response.json()
            except json.JSONDecodeError:
                return {"error": "Invalid JSON format"}
        else:
            return {"error": f"File not found or access denied (Status: {response.status_code})"}
    except Exception as e:
        return {"error": str(e)}

# Lista para almacenar datos para el Excel
excel_data = []

for proceso in procesos:
    proceso_id = proceso["id"]
    proceso_name = proceso["name"]
    repos = get_all_projects(proceso_id)

    proceso_info = {
        "proceso_id": proceso_id,
        "proceso_name": proceso_name,
        "repositorios": []
    }

    for repo in repos:
        # Obtener el contenido del project.json
        project_json = get_project_json_content(repo["id"])
        
        repo_data = {
            "repo_id": repo["id"],
            "repo_name": repo["name"],
            "repo_url": repo["web_url"],
            "project_json": project_json
        }
        proceso_info["repositorios"].append(repo_data)

        # Extraer información relevante del project.json para el Excel
        project_name = project_json.get("name", "N/A")
        project_version = project_json.get("version", "N/A")
        project_description = project_json.get("description", "N/A")
        
        # Agregar a la lista para el Excel
        excel_data.append([
            proceso_name,
            repo["name"],
            repo["web_url"],
            project_name,
            project_version,
            project_description
        ])

    data["procesos"].append(proceso_info)

# Detectar carpeta de descargas según el sistema operativo
if os.name == "nt":  # Windows
    download_path = os.path.join(os.path.expanduser("~"), "Downloads")
else:  # macOS / Linux
    download_path = os.path.join(os.path.expanduser("~"), "Descargas")

# Guardar JSON en Descargas
json_file_path = os.path.join(download_path, "procesos_no_aloe_repos.json")
with open(json_file_path, "w", encoding="utf-8") as f:
    json.dump(data, f, indent=4, ensure_ascii=False)

# Guardar Excel en Descargas
excel_file_path = os.path.join(download_path, "procesos_no_aloe_repos.xlsx")
df = pd.DataFrame(excel_data, columns=[
    "Proceso",
    "Repositorio",
    "Enlace",
    "Nombre Proyecto",
    "Versión",
    "Descripción"
])
df.to_excel(excel_file_path, index=False, engine="openpyxl")

# Confirmar guardado
print(f"\n✅ Archivo JSON guardado en: {json_file_path}")
print(f"✅ Archivo Excel guardado en: {excel_file_path}")

# Actualizar la visualización de los resultados
print("\n🔹 Repositorios y sus project.json:")
for proceso in data["procesos"]:
    print(f"\n📂 Proceso: {proceso['proceso_name']}")
    for repo in proceso["repositorios"]:
        print(f"   📌 Repo: {repo['repo_name']}")
        if isinstance(repo['project_json'], dict) and 'error' not in repo['project_json']:
            print(f"      📄 Nombre: {repo['project_json'].get('name', 'N/A')}")
            print(f"      📄 Versión: {repo['project_json'].get('version', 'N/A')}")
            print(f"      📄 Descripción: {repo['project_json'].get('description', 'N/A')}")
        else:
            print(f"      ❌ Error: {repo['project_json'].get('error', 'Error desconocido')}")
