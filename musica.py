import nextcord
from nextcord.ext import commands
from nextcord import SlashOption
import yt_dlp
import os
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv("DISCORD_KEY")

intents = nextcord.Intents.default()
intents.message_content = True
intents.voice_states = True
bot = commands.Bot(intents=intents)

@bot.event
async def on_ready():
    print(f"✅ Bot conectado como {bot.user}")

@bot.slash_command(name="join", description="Conectarme al canal de voz")
async def join(interaction: nextcord.Interaction):
    if interaction.user.voice:
        channel = interaction.user.voice.channel
        await channel.connect()
        await interaction.response.send_message("🎧 Me conecté al canal de voz", ephemeral=True)
    else:
        await interaction.response.send_message("❌ Debes estar en un canal de voz primero.", ephemeral=True)

@bot.slash_command(name="leave", description="Salir del canal de voz")
async def leave(interaction: nextcord.Interaction):
    if interaction.guild.voice_client:
        await interaction.guild.voice_client.disconnect()
        await interaction.response.send_message("👋 Me salí del canal de voz", ephemeral=True)
    else:
        await interaction.response.send_message("❌ No estoy conectado a ningún canal de voz.", ephemeral=True)

@bot.slash_command(
    name="play",
    description="Reproduce música desde YouTube",
)
async def play(
    interaction: nextcord.Interaction,
    query: str = SlashOption(description="Nombre de la canción o URL", required=True)
):
    await interaction.response.defer()  # Por si se demora

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

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(f"ytsearch1:{query}", download=False)
        if 'entries' in info:
            info = info['entries'][0]  # Primer resultado
        audio_url = info['url']
    vc.stop()
    vc.play(
        nextcord.FFmpegPCMAudio(audio_url, executable="ffmpeg"),
        after=lambda e: print(f"Finalizó con error: {e}") if e else None
    )

    await interaction.followup.send(f"▶️ Reproduciendo: {info['title']}")

bot.run(TOKEN)
