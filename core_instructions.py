from typing import Final
import os
from dotenv import load_dotenv
from discord import Intents, Client, Message
from responses import get_response, retrieve_weather

#STEP 0: LOAD OUR TOKEN FROM SOMEWHERE SAFE

# Load environment variables from a .env file into the program's environment
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
client: Client = Client(intents=intents)

# Step 2: receiving messages and sending
async def send_message(message: Message, user_message: str) -> None:
    # check if there is a user message
    if not user_message:
        print('(Message was empty because intents were not enabled)')
        return

    if is_private := user_message[0] == '?':
        user_message = user_message[1:] # string slicing to not include question mark
    
    try:
        response: str
        if user_message.startswith('weather'):
            city = user_message[len('weather '):].strip()
            response = retrieve_weather(city, WEATHER_API_KEY)
        else:
            response = get_response(user_message)
        await message.author.send(response) if is_private else await message.channel.send(response)
    except Exception as e:
        print(e)

# STEP 3: Startup for bot section
@client.event
async def on_ready() -> None:
    print(f'{client.user} is now running!')


# STEP 4: Handle incoming messages
@client.event
async def on_message(message: Message) -> None:
    if message.author == client.user:
        return
    
    user_message: str = message.content

    # FOR OUR EYES ONLY. AN EMERGENCY SHUTDOWN
    if user_message.lower() == '!shutdown' and message.author.guild_permissions.administrator:
        await message.channel.send("I'll be back...")
        await client.close()
        return

    # Only respond with a prefix of choie
    if user_message.startswith('.'):
        print(f'[Message] {message.author}: "{user_message}"')
        await send_message(message, user_message[1:]) # remove the . prefix before process

# STEP 5: Main entry point
def main() -> None:
    client.run(token=TOKEN)

if __name__ == '__main__':
    main()