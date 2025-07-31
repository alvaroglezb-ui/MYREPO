import requests
import os

# Asegúrate de tener la variable de entorno AZURE_FUNCTION_CODE configurada o reemplázala con tu código de función real
azure_function_code = "NncoxbWD-g9iTwCdonIeKOH4H_uG0BDtC1v4qisPr42oAzFua0C_Iw=="

# URL de la función de Azure
url = f"https://funcioncargadocumentos.azurewebsites.net/api/carga_doc?code={azure_function_code}"

# Ruta al archivo que deseas cargar
file_path = r"C:\Users\BD828FX\Desktop\Pruebas_P047_Extraccion\Test_Facturas_01\16062.pdf"

# Asegúrate de que el archivo existe
if not os.path.isfile(file_path):
    raise Exception(f"El archivo no existe: {file_path}")

# Abre el archivo en modo binario
with open(file_path, 'rb') as f:
    # Define los campos del formulario
    files = {
        'file': (os.path.basename(file_path), f, 'application/pdf'),
    }
    data = {
        'proceso': '4',
        'tipologia': '1',
        'type_ext':''
    }
    
    # Realiza la solicitud POST
    response = requests.post(url, files=files, data=data)
    
    # Verifica si la solicitud fue exitosa
    if response.status_code == 200:
        print("Archivo cargado con éxito.")
        print(response.content.decode('utf-8'))
    else:
        print(f"Error al cargar el archivo: {response.status_code} - {response.text}")
