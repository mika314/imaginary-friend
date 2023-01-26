from datetime import datetime
import asyncio
import discord
import glob
import os
import queue
import subprocess
import threading

intents = discord.Intents(messages=True, guilds=True, guild_messages=True, guild_reactions=True, message_content=True)

client = discord.Client(intents=intents)

@client.event
async def on_ready():
    print(f'{client.user} has connected to Discord!')

# Create a queue to store the image generation tasks
image_queue = queue.Queue()

# Create a function to handle the image generation tasks
def handle_image_generation():
    while True:
        prompt = image_queue.get()
        subprocess.run(['./run_txt2img.sh', prompt], check=True)
        images_path = '/home/mika/prj/stablediffusion/outputs/txt2img-samples/samples/'
        images = glob.glob(images_path + '*.png')
        images.sort(key=lambda x: os.path.getmtime(x))
        images = images[-9:]
        loop = asyncio.get_event_loop()
        for image in images:
            with open(image, 'rb') as f:
                coro = message.channel.send(file=discord.File(f))
                asyncio.run_coroutine_threadsafe(coro, loop)
        image_queue.task_done()

# Start the thread to handle the image generation tasks
image_thread = threading.Thread(target=handle_image_generation)
image_thread.start()

@client.event
async def on_message(message):
    if message.content.startswith('/img'):
        prompt = message.content[5:]
        print(f'> {prompt}')
        # Add the prompt to the image generation queue
        image_queue.put(prompt)

@client.event
async def on_raw_reaction_add(payload):
    if payload.user_id != client.user.id:
        if payload.emoji.name == '❌':
            message = await client.get_channel(payload.channel_id).fetch_message(payload.message_id)
            if message.author == client.user:
                await message.delete()


with open('token.dat', 'r') as file:
    token = file.read()
client.run(token)
