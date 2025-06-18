import nextcord
from nextcord.ext import commands
from dotenv import load_dotenv
import os
from google import genai
from google.genai import types
import yt_dlp

load_dotenv()
api_key = os.getenv("API_KEY")
client = genai.Client(api_key=api_key)

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

        vc.stop()
        vc.play(
            nextcord.FFmpegPCMAudio(audio_url, executable="ffmpeg"),
            after=lambda e: print(f"Finalizó con error: {e}") if e else None
        )

        await interaction.followup.send(f"▶️ Reproduciendo: {info['title']}")

    except Exception as e:
        await interaction.followup.send(f"❌ Error al consultar la IA: {e}")

# Ejecutar el bot
token = os.getenv('DISCORD_KEY')
bot.run(token)
