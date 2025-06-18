import nextcord
from nextcord.ext import commands
import os
import requests
import asyncio
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()
DISCORD_TOKEN = os.getenv("DISCORD_KEY")
ELEVEN_API_KEY = os.getenv("ELEVENLABS_API_KEY")
VOICE_ID = os.getenv("VOICE_ID")  # Puedes usar una voz clonada aquí

intents = nextcord.Intents.default()
intents.message_content = True
intents.voice_states = True

bot = commands.Bot(intents=intents)

@bot.event
async def on_ready():
    print(f"✅ Bot conectado como {bot.user}")

@bot.slash_command(name="voz", description="Reproduce una frase con voz realista")
async def voz(interaction: nextcord.Interaction, texto: str):
    await interaction.response.defer()

    # Llamar a ElevenLabs
    url = f"https://api.elevenlabs.io/v1/text-to-speech/{VOICE_ID}"
    headers = {
        "xi-api-key": ELEVEN_API_KEY,
        "Content-Type": "application/json"
    }
    payload = {
        "text": texto,
        "voice_settings": {
            "stability": 0.4,
            "similarity_boost": 0.8
        }
    }

    response = requests.post(url, headers=headers, json=payload)
    if response.status_code != 200:
        await interaction.followup.send("❌ Error al generar voz.")
        return

    with open("voz.mp3", "wb") as f:
        f.write(response.content)

    # Conectarse al canal de voz
    if interaction.user.voice:
        canal = interaction.user.voice.channel
        vc = await canal.connect()
        vc.play(nextcord.FFmpegPCMAudio("voz.mp3"))
        while vc.is_playing():
            await asyncio.sleep(1)  # <- Corrección aquí
        await vc.disconnect()
        await interaction.followup.send("🔊 Voz reproducida.")
    else:
        await interaction.followup.send("❌ Debes estar en un canal de voz.")

bot.run(DISCORD_TOKEN)
