# Importando las bibliotecas necesarias
from google import genai
from google.genai import types
import os
from dotenv import load_dotenv

# Cargar las variables de entorno desde el archivo .env
load_dotenv()

# Recuperar la API key desde el archivo .env
api_key = os.getenv("API_KEY")

# Crear el cliente de GenAI con la clave API
client = genai.Client(api_key=api_key)

# Leer el prompt desde el archivo
def leer_prompt_desde_archivo(archivo):
    try:
        with open(archivo, "r", encoding="utf-8") as f:
            return f.read().strip()  # Leer y eliminar espacios extra
    except FileNotFoundError:
        print("Error: No se encontró el archivo.")
        return None

def preguntar_gemini(prom,preguntas):
    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=f"{prom}{preguntas}"
        )
    
    return response.text

# Nombre del archivo de entrada
archivo_prompt = "prompt.txt"

# Leer y procesar el prompt
prompt = leer_prompt_desde_archivo(archivo_prompt)
pregunta = "\n\nHistoria: Rumpy mi wacho tengo un dilema me gusta mi mejor amiga pero me rechazo pero el otro día la invite a salir y estuvimos abrazados y la pasamos muy bien. Luego cuando me fui a despedir me dijo de verdad me quieres? y sipo obvio que la quiero y que la amo pero me confunde"
if prompt:
    respuesta1 = preguntar_gemini(prompt, pregunta)
    prompt2 = f"Esta es la Historia: {pregunta} y esta es la respuesta del locutor de la radio: {respuesta1} //// Ahora quiero que relaciones la historia con una cancion en español conocida ya sea latina o española. La respuesta que me tienes que dar es textualmente 'Te voy a ponerte un tema y este es nombredelacancion y nombre del artista'  "
    respuesta2 = preguntar_gemini(prompt2, "")
    print("Rumpy Responde:", respuesta1, " \n\n")
    print("Rumpy Responde:", respuesta2)
    #print("Rumpy Responde:", respuesta)

    

