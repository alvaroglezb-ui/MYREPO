import requests
import json
import os
import pandas as pd

# Configuración API de GitLab
GITLAB_URL = "https://fuentes.juntadeandalucia.es/api/v4"
PRIVATE_TOKEN = ""  # Reemplázalo con tu token

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

# Buscar el subgrupo PROCESOS
procesos_group = next((g for g in subgroups_automatismos if "PROCESOS" in g["name"].upper()), None)
if not procesos_group:
    print("🚨 No se encontró el subgrupo PROCESOS dentro de AUTOMATISMOS.")
    exit()

# Obtener todos los subgrupos dentro de PROCESOS (cada uno representa un proceso)
procesos = get_all_subgroups(procesos_group["id"])

# Verificar qué procesos se han detectado
print("\n🔹 Procesos detectados dentro de PROCESOS:")
for proceso in procesos:
    print(f"   - {proceso['name']} (ID: {proceso['id']}) - {proceso['full_path']}")

# Extraer repositorios de cada proceso
data = {
    "group_id": procesos_group["id"],
    "group_name": procesos_group["full_path"],
    "procesos": []
}

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
        repo_data = {
            "repo_id": repo["id"],
            "repo_name": repo["name"],
            "repo_url": repo["web_url"]
        }
        proceso_info["repositorios"].append(repo_data)

        # Agregar a la lista para el Excel
        excel_data.append([proceso_name, repo["name"], repo["web_url"]])

    data["procesos"].append(proceso_info)

# Detectar carpeta de descargas según el sistema operativo
if os.name == "nt":  # Windows
    download_path = os.path.join(os.path.expanduser("~"), "Downloads")
else:  # macOS / Linux
    download_path = os.path.join(os.path.expanduser("~"), "Descargas")

# Guardar JSON en Descargas
json_file_path = os.path.join(download_path, "procesos_repos.json")
with open(json_file_path, "w", encoding="utf-8") as f:
    json.dump(data, f, indent=4, ensure_ascii=False)

# Guardar Excel en Descargas
excel_file_path = os.path.join(download_path, "procesos_repos.xlsx")
df = pd.DataFrame(excel_data, columns=["Proceso", "Repositorio", "Enlace"])
df.to_excel(excel_file_path, index=False, engine="openpyxl")

# Confirmar guardado
print(f"\n✅ Archivo JSON guardado en: {json_file_path}")
print(f"✅ Archivo Excel guardado en: {excel_file_path}")

# Mostrar los repositorios extraídos
print("\n🔹 Repositorios dentro de cada proceso:")
for proceso in data["procesos"]:
    print(f"\n📂 Proceso: {proceso['proceso_name']}")
    for repo in proceso["repositorios"]:
        print(f"   📌 Repo: {repo['repo_name']} - {repo['repo_url']}")
