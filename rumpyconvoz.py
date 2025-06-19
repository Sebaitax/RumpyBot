import nextcord
from nextcord.ext import commands
from dotenv import load_dotenv
import os
from google import genai
from google.genai import types
import yt_dlp
import requests
import asyncio

load_dotenv()
api_key = os.getenv("API_KEY")
client = genai.Client(api_key=api_key)
ELEVEN_API_KEY = os.getenv("ELEVENLABS_API_KEY")
VOICE_ID = os.getenv("VOICE_ID")  # Puedes usar una voz clonada aquí

# Función para leer el prompt base desde archivo
def leer_prompt_desde_archivo(archivo):
    try:
        with open(archivo, "r", encoding="utf-8") as f:
            return f.read().strip()
    except FileNotFoundError:
        print("Error: No se encontró el archivo.")
        return ""

# Función para preguntar a Gemini
def preguntar_gemini(prom, preguntas):
    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=f"{prom}{preguntas}"
    )
    return response.text

# Leer prompt base
archivo_prompt = "prompt.txt"
prompt_base = leer_prompt_desde_archivo(archivo_prompt)

# ========== Discord Bot ==========
intents = nextcord.Intents.default()
intents.message_content = True
intents.voice_states = True
intents.members = True

bot = commands.Bot(intents=intents)

@bot.event
async def on_ready():
    print(f"✅ Bot conectado correctamente como {bot.user}")

@bot.slash_command(name="chat", description="Confiesate al Rumpy")
async def chat(interaction: nextcord.Interaction, consulta: str):
    await interaction.response.defer()  # Por si demora un poco

    if not prompt_base:
        await interaction.followup.send("❌ No se pudo cargar el prompt base.")
        return
    try:
        vc = interaction.guild.voice_client
        if not vc:
            if interaction.user.voice:
                channel = interaction.user.voice.channel
                vc = await channel.connect()
            else:
                await interaction.followup.send("❌ Debes estar en un canal de voz para reproducir música.")
                return
        
        ydl_opts = {
        'format': 'bestaudio',
        'quiet': True,
        'default_search': 'ytsearch',
        'noplaylist': True,
        }
        
        respuesta = preguntar_gemini(prompt_base, f"\n\nHistoria: {consulta}")
        prompt2 = f"Esta es la Historia: {consulta} y esta es la respuesta del locutor de la radio: {respuesta} //// Ahora quiero que relaciones la historia con una cancion en español conocida ya sea latina o española. La respuesta que me tienes que dar es textualmente 'nombredelacancion de nombredelartista'  "
        respuesta2 = preguntar_gemini(prompt2, "")
        """ 
        temaEsta = preguntar_gemini("gemini si la siguiente cancion existe dame la respuesta si o no. Cancion: ", f"{respuesta2}")
        while  "si" not in temaEsta:
            respuesta2 = preguntar_gemini("Gemini te hice la siguiente consulta antes y me dio una canción que no existe. Hacela denuevo. Consulta anterior:", prompt2)
            temaEsta = preguntar_gemini("gemini si la siguiente cancion existe dame la respuesta si o no. Cancion: ", f"{respuesta2}")
        """
        MAX_LEN = 1000
        fragmentos = [respuesta[i:i + MAX_LEN] for i in range(0, len(respuesta), MAX_LEN)]
        await interaction.followup.send(f"confesion: {consulta}\n")
        
        # Enviar los fragmentos uno a uno
        for i, fragmento in enumerate(fragmentos):
            if i == 0:
             await interaction.followup.send(f"{fragmento}")
            else:
                await interaction.followup.send(fragmento)
        

        await interaction.followup.send(f"\n{respuesta2}")

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(f"ytsearch1:{respuesta2}", download=False)
            if 'entries' in info:
                info = info['entries'][0]
            audio_url = info['url']

        
        # Llamar a ElevenLabs
        url = f"https://api.elevenlabs.io/v1/text-to-speech/{VOICE_ID}"
        headers = {
            "xi-api-key": ELEVEN_API_KEY,
            "Content-Type": "application/json"
        }
        payload = {
            "text": f"{respuesta} y te voy a ponerte un tema y este es {respuesta2}",
            "voice_settings": {
                "stability": 0.4,
                "similarity_boost": 0.8
            }
        }
        response = requests.post(url, headers=headers, json=payload)
        if response.status_code != 200:
            await interaction.followup.send("❌ Error al generar voz.")
            return
        
        """    
        ### INTRO
        vc.play(nextcord.FFmpegPCMAudio("intro.mp3"))
        while vc.is_playing():
            await asyncio.sleep(1)
        """

        ###VOOOOZ
        with open("voz.mp3", "wb") as f:
            f.write(response.content)
        vc.play(nextcord.FFmpegPCMAudio("voz.mp3"))
        while vc.is_playing():
            await asyncio.sleep(1)

        vc.stop()
        vc.play(
            nextcord.FFmpegPCMAudio(audio_url, executable="ffmpeg"),
            after=lambda e: print(f"Finalizó con error: {e}") if e else None
        )
        while vc.is_playing():
            await asyncio.sleep(1)

        await interaction.followup.send(f"▶️ Reproduciendo: {info['title']}")

    except Exception as e:
        await interaction.followup.send(f"❌ Error al consultar la IA: {e}")

# Ejecutar el bot
token = os.getenv('DISCORD_KEY')
bot.run(token)
