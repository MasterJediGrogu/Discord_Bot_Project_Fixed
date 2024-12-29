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
@bot.tree.command(name="shutdown", description= "Shutdown the bot. (Admin USE only) CAUTION: Will shutdown other instances. Contact system admin")
async def shutdown(interaction: Interaction):
    # check if user has Administrator or Manage Channels Permissions

    #DEBUG
    print(f'User {interaction.user} Permissions: {interaction.user.guild_permissions}')

    if (interaction.user.guild_permissions.adminstrator or
        interaction.user.guild_permissions.manage_channels):
        await interaction.response.send_message("Shutting down...")
        await bot.close() # Shutdown the bot
    else:
        # Find roles with either Admin or Manage Channel permission to alert admin team
        #DEBUG: Which permission failed:
        print(f'User {interaction.user} lacks required permissions. Adminstrator or Manage Channels')
        eligible_roles = [
            role for role in interaction.guild.roles
            if role.permissions.adminstrator or role.permissions.manage_channels
        ]

        if eligible_roles:
            # Mention all roles with the permission
            role_mentions = ", ".join([role.mention for role in eligible_roles])
            alert_message= (
                f" **Unauthorized Shutdown Attempt** \n"
                f" User {interaction.user.mention} tried to SHUT ME DOWN!! \n"
                f" Alert: {role_mentions}"
            )
            # Alert the channel user is inS
            await interaction.response.send_message(
                f" You don't have permission to shut me down. Alerting: {role_mentions}"
            )
            await interaction.channel.send(alert_message)
        else:
            # If no roles were found with the required permissions
            await interaction.response.send_message(
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