import requests
import json

# Configuración API de GitLab
GITLAB_URL = "https://fuentes.juntadeandalucia.es/api/v4"
PRIVATE_TOKEN = "glpat-Y3NgGBAQtYUhM2YzjECD"  # Reemplázalo con tu token

# ID directo de AUTOMATISMOS
AUTOMATISMOS_GROUP_ID = 645  # ID obtenido previamente

# Cabecera para autenticación
HEADERS = {"Private-Token": PRIVATE_TOKEN}

# Función para obtener subgrupos de un grupo
def get_subgroups(group_id):
    url = f"{GITLAB_URL}/groups/{group_id}/subgroups"
    response = requests.get(url, headers=HEADERS)
    return response.json() if response.status_code == 200 else []

# Función para obtener los proyectos de un grupo
def get_projects(group_id):
    url = f"{GITLAB_URL}/groups/{group_id}/projects"
    response = requests.get(url, headers=HEADERS)
    return response.json() if response.status_code == 200 else []

# Obtener subgrupos dentro de AUTOMATISMOS (debería incluir PROCESOS)
subgroups_automatismos = get_subgroups(AUTOMATISMOS_GROUP_ID)

# Buscar el subgrupo PROCESOS
procesos_group = next((g for g in subgroups_automatismos if "PROCESOS" in g["name"].upper()), None)
if not procesos_group:
    print("🚨 No se encontró el subgrupo PROCESOS dentro de AUTOMATISMOS.")
    exit()

# Obtener todos los subgrupos dentro de PROCESOS (cada uno representa un proceso)
procesos = get_subgroups(procesos_group["id"])

# Extraer repositorios de cada proceso
data = {
    "group_id": procesos_group["id"],
    "group_name": procesos_group["full_path"],
    "procesos": []
}

for proceso in procesos:
    proceso_id = proceso["id"]
    proceso_name = proceso["name"]
    repos = get_projects(proceso_id)

    data["procesos"].append({
        "proceso_id": proceso_id,
        "proceso_name": proceso_name,
        "repositorios": [
            {"repo_id": repo["id"], "repo_name": repo["name"], "repo_url": repo["web_url"]}
            for repo in repos
        ]
    })

# Guardar los datos en un archivo JSON
with open("procesos_repos.json", "w", encoding="utf-8") as f:
    json.dump(data, f, indent=4, ensure_ascii=False)

# Imprimir resultados
print("\n🔹 Repositorios dentro de cada proceso:")
for proceso in data["procesos"]:
    print(f"\n📂 Proceso: {proceso['proceso_name']}")
    for repo in proceso["repositorios"]:
        print(f"   📌 Repo: {repo['repo_name']} - {repo['repo_url']}")
