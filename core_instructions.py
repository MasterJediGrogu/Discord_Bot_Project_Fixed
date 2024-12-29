from typing import Final
import os
from dotenv import load_dotenv
from discord import Intents, Interaction
from discord.ext import commands
from responses import retrieve_weather

#STEP 0: LOAD OUR TOKEN FROM SOMEWHERE SAFE

# Load environment variables from a .env file int o the program's environment
load_dotenv()

# Get the value of the "DISCORD_TOKEN" env. variable
# and assign it to the TOKEN variable. The Final[str] type hint indicates that
# TOKEN should not be reassigned and is expected to be of type str
TOKEN: Final[str] = os.getenv('DISCORD_TOKEN')
# print(TOKEN)   (remove for debugging purposes, not necessary though)
# Get the value of the "WEATHER_API_KEY" env. variable
WEATHER_API_KEY: Final[str] = os.getenv('WEATHER_API_KEY')

# Step 1: BOT SETUP

intents: Intents = Intents.default()
intents.message_content = True #NOQA
bot = commands.Bot(command_prefix=".", intents=intents)

# ==========================================================================================================
# (WEATHER SECTION)
# the inclusion of defining a slash command for weather
@bot.tree.command(name="weather", description="Get Current Weather Information for a City")
async def weather(interaction: Interaction, city: str):
  #  """Handling the /weather slash command process here."""
    try:
        response = retrieve_weather(city, WEATHER_API_KEY)
        await interaction.response.send_message(response)
    except Exception as e:
        print(f'Error Retrieving Weather: {e}')
        await interaction.response.send_message("Sorry, I could not get the weather. Please try again.")

# ==========================================================================================================

# (ADMIN SECTION)

#                                         =Shutdown Command=
@bot.tree.command(name="shutdown", description="Shutdown the bot. (Admin Use only) CAUTION: Will shut down other instances.")
async def shutdown(interaction: Interaction):
    """
    Shuts down the bot if the user has Administrator or Manage Channels permissions.
    Dynamically checks for roles with these permissions and alerts them if a non-eligible user attempts to shut down.
    """
    # DEBUG: Log user permissions
    print(f'User {interaction.user} Permissions: {interaction.user.guild_permissions}')

    # Acknowledge the interaction immediately
    await interaction.response.defer()

    # Check if the user has the required permissions
    if interaction.user.guild_permissions.administrator or interaction.user.guild_permissions.manage_channels:
        await interaction.followup.send("Shutting down...")
        await bot.close()  # Shutdown the bot
    else:
        # DEBUG: Which permission failed
        print(f'User {interaction.user} lacks required permissions: Administrator or Manage Channels')

        # Find roles with either Administrator or Manage Channels permission to alert admin team
        eligible_roles = [
            role for role in interaction.guild.roles
            if role.permissions.administrator or role.permissions.manage_channels
        ]

        if eligible_roles:
            # Mention all roles with the permissions
            role_mentions = ", ".join([role.mention for role in eligible_roles])
            alert_message = (
                f"🚨 **Unauthorized Shutdown Attempt** 🚨\n"
                f"User {interaction.user.mention} tried to shut down the bot.\n"
                f"Alerting: {role_mentions}"
            )

            # Send alert to the channel
            await interaction.followup.send(
                f"You don't have permission to shut me down! Alerting: {role_mentions}"
            )
            await interaction.channel.send(alert_message)
        else:
            # If no roles were found with the required permissions
            await interaction.followup.send(
                "You don't have permission to shut me down. No roles to alert were found."
            )
# ==========================================================================================================


# ==========================================================================================================
# (STARTUP SECTION)
@bot.event
async def on_ready():
    try:
        await bot.tree.sync() # sync all the slash commands
        print(f'Bot is ready and logged in as {bot.user}')
    except Exception as e:
        print(f'Error syncing commands: {e}')
# ==========================================================================================================

# ==========================================================================================================
# (MAIN ENTRY POINT)
def main():
    bot.run(TOKEN)

if __name__ == '__main__':
    main()
# ==========================================================================================================
