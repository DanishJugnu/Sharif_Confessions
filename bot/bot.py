import discord
from discord import app_commands
from discord import SyncWebhook
from discord.ext import commands
from discord.ui import Modal, Select, View
import aiohttp
from data import *
import json
import asyncio
import traceback

# for my dotenv file
#from decouple import config


intents = discord.Intents.default()

bot = commands.Bot(command_prefix="!!", case_insensitive=True, intents=intents,
                   strip_after_prefix=True)

slash = bot.tree


class Body(Modal, title='Anonymous Message Editor'):
    content = discord.ui.TextInput(
        label="'Message'",
        style=discord.TextStyle.long,
        placeholder='The text that will become your anonymous message',
        required=True,
        max_length=4000,
    )

    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.defer()

    async def on_error(self, error: Exception, interaction: discord.Interaction) -> None:
        await interaction.response.send_message(f'Oops! Something went wrong.\nError: {error}', ephemeral=True)

        # Make sure we know what the error actually is
        traceback.print_tb(error.__traceback__)


class Dropdown(Select):
    def __init__(self):

        with open("storage.json", "r") as f:
            data = json.load(f)

        options = [discord.SelectOption(label=k) for k in data["blocked_anon_numbers"]]

        # The placeholder is what will be shown when no option is chosen
        # The min and max values indicate we can only pick one of the three options
        # The options parameter defines the dropdown options. We defined this above
        super().__init__(placeholder='Choose the anon_id_number...', min_values=1, max_values=1, options=options)

    async def callback(self, interaction: discord.Interaction):
        self.view.val = True
        self.view.stop()


class DropdownView(View):
    def __init__(self):
        self.val = False
        super().__init__(timeout=60)

        # Adds the dropdown to our view object.
        self.add_item(Dropdown())

    async def on_timeout(self):
        return


@bot.event
async def on_ready():
    print("Bot running with:")
    print("Username: ", bot.user.name)
    print("User ID: ", bot.user.id)
    await slash.sync(guild=discord.Object(id=GUILD_ID))


@slash.command(guild=discord.Object(id=GUILD_ID))
@app_commands.describe(
    content='The text of your anonymous message, leave blank for a paragraph editor',
)
async def confess(interaction, content: str = None):
    """Send an anonymous message to this channel"""
    # Remove the next two lines to let slash command be used in any channel
    #if not interaction.channel_id == CHANNEL_ID:
     #   return

    with open("storage.json", "r") as f:
        data = json.load(f)

    # Blocked Check
    if interaction.user.id in data["blocked"]:
        return await interaction.response.send_message("You have been blocked from confessing.", ephemeral=True)

    emb = discord.Embed(color=discord.Color.random(), title="Sharif Sabha")
    data["count"] += 1
    emb.set_footer(text=f"Conferssion no. #{data['count']}, If this confession is ToS-breaking or overtly hateful, you can report it ")
    emb.set_thumbnail(url="https://cdn.discordapp.com/icons/1104365324582793318/a_7457fcf4ca011dd5db45a0ebb069dcea.gif")

    with open("storage.json", "w") as f:
        json.dump(data, f, indent=4)

    option = False
        # Take long input
    modal = Body()
    await interaction.response.send_modal(modal)
    option = await modal.wait()
    if option:
        return
    content = str(modal.content)
    option = True

    if content:
        emb.description = f'"{content}"'

    if option:
        await interaction.followup.send("Done, your Confession has been submited.", ephemeral=True)
    else:
        await interaction.response.send_message("Done, your confession has been submited.", ephemeral=True)

    ch = interaction.guild.get_channel(CHANNEL_ID)
    await ch.send(embed=emb)

    #ch = interaction.guild.get_channel(channel_id)
    #username = interaction.user
    #await ch.send(f'Confession Log:\nUsername: {username}\n\n{str(emb)}')

    username = interaction.user
    description = emb.description
    confession_number = data["count"]

    confession_embed = discord.Embed(
    title="Confession Log",
    description=f"Confession Number: {confession_number}\nUsername: {username}\nDescription: {description}",
    color=discord.Color.random()
    )
    webhook = SyncWebhook.from_url('YOUR WEBHOOK URL')
    webhook.send(embed=confession_embed)

bot.run("BOT_TOKEN")  # Replace with your Discord bot token