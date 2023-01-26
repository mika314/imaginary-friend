from datetime import datetime
import discord
import glob
import os
import subprocess

intents = discord.Intents(messages=True, guilds=True, guild_messages=True, guild_reactions=True, message_content=True)

client = discord.Client(intents=intents)

@client.event
async def on_ready():
    print(f'{client.user} has connected to Discord!')

@client.event
async def on_message(message):
    if message.content.startswith('/img'):
        prompt = message.content[5:]
        print(f'> {prompt}')
        # run the command here, using the prompt variable to fill in the [prompt] argument
        subprocess.run(['./run_txt2img.sh', prompt], check=True)
        # upload the generated images to Discord and add the prompt and X emote
        images_path = '/home/mika/prj/stablediffusion/outputs/txt2img-samples/samples/'
        images = glob.glob(images_path + '*.png')
        images.sort(key=lambda x: os.path.getmtime(x))
        images = images[-9:]
 
        for image in images:
            with open(image, 'rb') as f:
                sent_message = await message.channel.send(file=discord.File(f))
                await sent_message.add_reaction('❌')
        
    if message.content.startswith('/delete'):
        # check if the message has an X emote and delete it if necessary
        pass

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
