import os
import tempfile
from datetime import datetime
import asyncio
import discord
import glob
import os
import queue
import subprocess
import threading
import requests

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
        prompt, message, isWaifu, image_path = image_queue.get()
        try:
            if isWaifu:
                subprocess.run(['./run_waifu_txt2img.sh', prompt, image_path], check=True)
            else:
                subprocess.run(['./run_txt2img.sh', prompt, image_path], check=True)
            images_path = '/home/mika/prj/stablediffusion/outputs/txt2img-samples/samples/'
            if image_path == "":
                images = glob.glob(images_path + '*.png')
                images.sort(key=lambda x: os.path.getmtime(x))
                images = images[-9:]
                coro = send_images(message.channel, images, prompt)
                asyncio.ensure_future(coro, loop=client.loop)
            else:
                images_path = '/home/mika/prj/stablediffusion/outputs/img2img-samples/samples/'
                images = glob.glob(images_path + '*.png')
                images.sort(key=lambda x: os.path.getmtime(x))
                images = images[-4:]
                coro = send_images(message.channel, images, prompt)
                asyncio.ensure_future(coro, loop=client.loop)
        except subprocess.CalledProcessError as e:
            # Handle the error
            error_message = f"Error generating image: {e}\nPlease try again later or contact the administrator."
            asyncio.ensure_future(message.channel.send(error_message), loop=client.loop)
        image_queue.task_done()

# Start the thread to handle the image
threading.Thread(target=handle_image_generation, daemon=True).start()

@client.event
async def on_message(message):
    if message.content.startswith('/img'):
        prompt = message.content[5:]
        print(f'> {prompt}')
        await message.channel.send(f"Prompt \"{prompt}\" is queued...")
        # check if message has an embedded image
        if message.attachments:
            # download the image
            image_url = message.attachments[0].url
            image_extension = os.path.splitext(image_url)[-1]
            with requests.get(image_url, stream=True) as r:
                r.raise_for_status()
                with tempfile.NamedTemporaryFile(suffix=image_extension, delete=False) as f:
                    for chunk in r.iter_content(chunk_size=8192):
                        f.write(chunk)
                    image_path = f.name
            # add the image path to the queue
            image_queue.put((prompt, message, False, image_path))
        else:
            image_queue.put((prompt, message, False, ""))
    if message.content.startswith('/waifu'):
        prompt = message.content[7:]
        print(f'> Waifu {prompt}')
        await message.channel.send(f"Waifu \"{prompt}\" is queued...")
        # check if message has an embedded image
        if message.attachments:
            # download the image
            image_url = message.attachments[0].url
            image_extension = os.path.splitext(image_url)[-1]
            with requests.get(image_url, stream=True) as r:
                r.raise_for_status()
                with tempfile.NamedTemporaryFile(suffix=image_extension, delete=False) as f:
                    for chunk in r.iter_content(chunk_size=8192):
                        f.write(chunk)
                    image_path = f.name
            # add the image path to the queue
            image_queue.put((prompt, message, True, image_path))
        else:
            image_queue.put((prompt, message, True, ""))

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
