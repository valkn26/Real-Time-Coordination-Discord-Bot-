import discord
from discord.ext import commands
import os
from dotenv import load_dotenv, find_dotenv
from datetime import datetime
import sys

# Load environment variables
env_path = find_dotenv('config.env')
if not env_path:
    print("Error: config.env file not found!")
    sys.exit(1)

if not load_dotenv(env_path):
    print("Error: Failed to load environment variables!")
    sys.exit(1)

if not os.getenv('DISCORD_BOT_TOKEN'):
    print("Error: DISCORD_BOT_TOKEN not found in environment variables!")
    sys.exit(1)

# Intents are required for certain events
intents = discord.Intents.default()
intents.message_content = True
intents.members = True

# Create a bot instance
bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f'Bot is ready.')
    print(f'Logged in as {bot.user.name}')

# Error handling
@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandOnCooldown):
        await ctx.send(f"Please wait {error.retry_after:.2f}s before using this command again.")
    elif isinstance(error, commands.MissingPermissions):
        await ctx.send("You don't have permission to use this command.")
    else:
        await ctx.send(f"An error occurred: {str(error)}")

# Active hunts storage
active_hunts = {}

@bot.command(name="hunt", help="Start a hunting session!")
@commands.cooldown(1, 60, commands.BucketType.user)
async def hunt(ctx, monster_name: str, player_count: int = 4):
    # Get the user's nickname or username
    hunter_name = ctx.author.nick if ctx.author.nick else ctx.author.name

    # Validate player count
    if not 1 <= player_count <= 4:
        await ctx.send("Player count must be between 1 and 4!")
        return

    hunt_id = f"{ctx.author.id}-{datetime.now().strftime('%Y%m%d%H%M%S')}"
    active_hunts[hunt_id] = {
        "leader": ctx.author,
        "monster": monster_name,
        "players": [ctx.author],
        "max_players": player_count,
        "status": "recruiting"
    }

    # Create the announcement message
    announcement = (
        f"🚨 **{hunter_name}** is organizing a hunt for **{monster_name}**! 🚨\n"
        f"Looking for {player_count - 1} more hunters!\n"
        f"React with 👍 to join!"
    )
    
    msg = await ctx.send(announcement)
    await msg.add_reaction("👍")

# Run the bot with token from environment variable
bot.run(os.getenv('DISCORD_BOT_TOKEN'))
