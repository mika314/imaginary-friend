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

async def send_images(channel, images, prompt):
    for image in images:
        print(f"uploading the image {image}")
        with open(image, 'rb') as f:
            sent_message = await channel.send(file=discord.File(f), content=f"Prompt: \"{prompt}\"")
            await sent_message.add_reaction('❌')

# Create a function to handle the image generation tasks
def handle_image_generation():
    while True:
        prompt, message, isWaifu = image_queue.get()
        if isWaifu:
            subprocess.run(['./run_waifu_txt2img.sh', prompt], check=True)
        else:
            subprocess.run(['./run_txt2img.sh', prompt], check=True)
        images_path = '/home/mika/prj/stablediffusion/outputs/txt2img-samples/samples/'
        images = glob.glob(images_path + '*.png')
        images.sort(key=lambda x: os.path.getmtime(x))
        images = images[-9:]
        coro = send_images(message.channel, images, prompt)
        asyncio.ensure_future(coro, loop=client.loop)
        image_queue.task_done()

# Start the thread to handle the image
threading.Thread(target=handle_image_generation, daemon=True).start()

@client.event
async def on_message(message):
    if message.content.startswith('/img'):
        prompt = message.content[5:]
        print(f'> {prompt}')
        await message.channel.send(f"Prompt \"{prompt}\" is queued...")
        image_queue.put((prompt, message, False))
    if message.content.startswith('/waifu'):
        prompt = message.content[7:]
        print(f'> Waifu {prompt}')
        await message.channel.send(f"Waifu \"{prompt}\" is queued...")
        image_queue.put((prompt, message, True))

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
