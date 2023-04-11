import discord
from discord.ext import commands
import openai
import asyncio
import random
from discord.utils import get

TOKEN = "TOKEN"
intents = discord.Intents.all()

client = commands.Bot(command_prefix='.', intents=intents)

openai.api_key = "API-Key"


@client.command()
async def chat(ctx, *, message):
    response = openai.Completion.create(
        engine="davinci", prompt=message, max_tokens=50
    )
    await ctx.send(response.choices[0].text)


@client.event
async def on_ready():
    print(f'{client.user.name} has connected to Discord!')


@client.event
async def on_member_join(member):
    channel = discord.utils.get(member.guild.channels, name="important-messages")
    await channel.send(f"Welcome to {member.guild.name}, {member.mention}!")


@client.event
async def on_member_remove(member):
    channel = discord.utils.get(member.guild.channels, name="important-messages")
    await channel.send(f"{member.mention} has left {member.guild.name}. Goodbye!")


@client.command()
async def ping(ctx):
    latency = client.latency
    await ctx.send(f"{latency * 1000:.2f} ms")


@client.command()
async def nickname(ctx, member: discord.Member, new_nickname: str):
    await member.edit(nick=new_nickname)  # edit the member's nickname
    await ctx.send(f"Changed {member}'s nickname to {new_nickname}")


@client.command()
async def hello(ctx):
    await ctx.send(f'Hello, {ctx.author.name}!')


@client.command()
async def roll(ctx):
    import random
    num = random.randint(1, 6)
    await ctx.send(f'{ctx.author.name} rolled a {num}!')


@client.command()
async def memberinfo(ctx):
    for member in ctx.guild.members:
        roles = [role.name for role in member.roles]
        activity = member.activity.name if member.activity else None
        await ctx.send(f"Member: {member.name}\nActivity: {activity}\nRoles: {roles}\nUser Status: {member.status}"
                       f"Hashtag: {member.discriminator}\nCreated At: {member.created_at}")


@client.command()
async def userinfo(ctx, member: discord.Member = None):
    # Displays information about the user who executed the command or another specified member.
    if member is None:
        user = ctx.author
    else:
        user = member
    user_info = f'Username: {user.name}\nDiscriminator: {user.discriminator}\nCreated At: {user.created_at}\n'
    if user.nick is not None:
        user_info += f'Nickname: {user.nick}\n'
    if user.joined_at is not None:
        user_info += f'Joined Server At: {user.joined_at}\n'
    user_info += f'Roles: {", ".join([role.mention for role in user.roles[1:]])}\n'
    user_info += f'Status: {user.status}\n'
    await ctx.send(user_info)


@client.command()
async def serverinfo(ctx):
    # Displays information about the server.
    server = ctx.guild
    server_info = f'Server Name: {server.name}\nServer ID: {server.id}\n' \
                  f'Member Count: {server.member_count}\n'
    await ctx.send(server_info)


@client.command()
@commands.has_permissions(kick_members=True)
async def kick(ctx, member: discord.Member, *, reason=None):
    await ctx.message.delete()

    # Check if the member is the bot owner
    if member.id == 371640321668546573:
        # Check if the invoker is the bot owner
        if ctx.author.id == 371640321668546573:
            await ctx.send("You can't kick the Bot owner.")
            return
        else:
            await ctx.send(f"You tried to kick {member.display_name}, but instead you will be kicked in 5 seconds for"
                           f" trying to kick the Bot owner.")
            await asyncio.sleep(5)
            await ctx.author.kick()  # Kick the command invoker instead of the member
    else:
        await ctx.send(f"{member.display_name} has been kicked from the server for try to kick the Bot owner.")
        await member.kick(reason=reason)

    # Kicks a user from the server with a specified reason.
    await member.kick(reason=reason)
    await ctx.send(f'{member} has been kicked. Reason: {reason}')


@client.command()
@commands.has_permissions(ban_members=True)
async def ban(ctx, member: discord.Member, *, reason=None):
    await ctx.message.delete()
    # Check if the member is the bot owner
    if member.id == 371640321668546573:
        await ctx.send("You can't ban the Bot owner.")
        warning_msg = f"{ctx.author.mention}, you cannot ban the Bot owner!"
        await ctx.send(warning_msg)
        return

    # Check if the bot has permission to ban the member
    if not member.guild.me.guild_permissions.ban_members:
        await ctx.send(f"I don't have permission to ban {member.mention}.")
        return

    # Bans a user from the server with a specified reason.
    await member.ban(reason=reason)
    await ctx.send(f'{member} has been banned. Reason: {reason}')


@client.command()
@commands.has_permissions(manage_roles=True)
async def mute(ctx, member: discord.Member, duration, *, reason=None):
    await ctx.message.delete()
    # Check if the member is the bot owner
    if member.id == 371640321668546573:
        await ctx.send("You can't mute the Bot owner.")
        warning_msg = f"{ctx.author.mention}, you cannot mute the Bot owner!"
        await ctx.send(warning_msg)
        return

    # Create muted role if it doesn't exist
    role = discord.utils.get(ctx.guild.roles, name='Muted')
    if not role:
        role = await ctx.guild.create_role(name='Muted')
        for channel in ctx.guild.channels:
            await channel.set_permissions(role, send_messages=False)

    await member.add_roles(role)
    await ctx.send(f'{member} has been muted for {duration}. Reason: {reason}')
    await asyncio.sleep(duration)
    await member.remove_roles(role)
    await ctx.send(f'{member} has been unmuted.')


@client.command()
@commands.has_permissions(manage_roles=True)
async def unmute(ctx, member: discord.Member):
    await ctx.message.delete()
    # Unmutes a previously muted user in the server.
    role = discord.utils.get(ctx.guild.roles, name='Muted')
    await member.remove_roles(role)
    await ctx.send(f'{member} has been unmuted.')


@client.command()
@commands.has_permissions(manage_messages=True)
async def purge(ctx, num: int):
    # Deletes a specified number of messages from a channel.
    await ctx.channel.purge(limit=num)


@client.command()
async def quote(ctx, message_id: int):
    try:
        message = await ctx.channel.fetch_message(message_id)
    except discord.errors.NotFound:
        await ctx.send(f"Message with ID {message_id} not found.")
        return

    # Format the message content
    content = message.content.replace("`", "'")

    # Send the formatted message as a quote
    await ctx.send(f"> {content}\n- {message.author.mention}")


@client.command()
async def join(ctx):
    # Check if the command author is in a voice channel
    if ctx.author.voice is None:
        await ctx.send("You are not in a voice channel.")
        return

    # Join the voice channel of the command author
    voice_channel = ctx.author.voice.channel
    await voice_channel.connect()
    await ctx.send(f"Joined {voice_channel}")


@client.command()
async def leave(ctx):
    # Check if the bot is in a voice channel
    if ctx.voice_client is None:
        await ctx.send("I am not in a voice channel.")
        return

    # Leave the current voice channel
    await ctx.voice_client.disconnect()
    await ctx.send("Left voice channel.")


@client.command()
async def addrole(ctx, member: discord.Member, role_name: str):
    # Get the role object from the server
    role = discord.utils.get(ctx.guild.roles, name=role_name)

    if role is None:
        await ctx.send(f"Role '{role_name}' not found.")
    else:
        # Add the role to the member
        await member.add_roles(role)
        await ctx.send(f"Added role '{role_name}' to {member.display_name}.")


@client.command()
async def deleterole(ctx, role_name: str):
    # Get the role object from the server
    role = discord.utils.get(ctx.guild.roles, name=role_name)

    if role is None:
        await ctx.send(f"Role '{role_name}' not found.")
    else:
        # Delete the role
        await role.delete()
        await ctx.send(f"Role '{role_name}' has been deleted.")


@client.command()
async def removerole(ctx, member: discord.Member, role_name: str):
    # Get the role object from the server
    role = discord.utils.get(ctx.guild.roles, name=role_name)

    if role is None:
        await ctx.send(f"Role '{role_name}' not found.")
    else:
        # Remove the role from the member
        await member.remove_roles(role)
        await ctx.send(f"Removed role '{role_name}' from {member.display_name}.")


@client.command()
async def create_role(ctx, member: discord.Member, role_name: str, color: str):
    # Check if the user has the necessary permissions to manage roles
    if not ctx.author.guild_permissions.manage_roles:
        await ctx.send("You do not have the necessary permissions to manage roles.")
        return

    # Check if the role already exists
    role = discord.utils.get(ctx.guild.roles, name=role_name)
    if role is not None:
        await ctx.send(f"The role {role_name} already exists.")
        return

    # Create the role with the specified color
    try:
        color = int(color, 16)
    except ValueError:
        await ctx.send("Invalid color format. Please use a hexadecimal color code (e.g. \n"
                       "#000000 - black\n"
                       "#FFFFFF - white\n"
                       "#FF0000 - red\n"
                       "#00FF00 - green\n"
                       "#0000FF - blue\n"
                       "#FFFF00 - yellow\n"
                       "#FF00FF - magenta\n"
                       "#00FFFF - cyan).")
        return
    role = await ctx.guild.create_role(name=role_name, color=discord.Color(color))

    # Add the role to the member
    await member.add_roles(role)

    await ctx.send(f"The role {role_name} has been created with color {color} and added to {member.display_name}.")


@client.command()
async def delete_channel(ctx, channel_name):
    for channel in ctx.guild.channels:
        if channel.name == channel_name:
            await channel.delete()
    await ctx.send(f"All channels with the name {channel_name} have been deleted.")


@client.command()
async def delete_role(ctx, role_name: str):
    try:
        # Find all roles with the same name
        roles = [role for role in ctx.guild.roles if role.name == role_name]
        if not roles:
            raise Exception(f"No roles named '{role_name}' were found.")

        # Delete each role
        count = 0
        for role in roles:
            await role.delete()
            count += 1

        await ctx.send(f"All roles named '{role_name}' have been deleted from the server ({count} roles deleted).")
    except Exception as e:
        await ctx.send(f"An error occurred: {e}")


# @client.command()
# async def rickroll(ctx):
# Check if the author is connected to a voice channel
#    if ctx.author.voice is None:
#        await ctx.send("You need to be in a voice channel to use this command!")
#        return
#    source = discord.PCMVolumeTransformer(discord.FFmpegPCMAudio("https://www.youtube.com/watch?v=dQw4w9WgXcQ"))
#    player = ctx.voice_client
#    player.play(source)
#    while player.is_playing():
#        await asyncio.sleep(1)
#    await player.disconnect()

@client.command()
async def menu(ctx):
    embed = discord.Embed(
        title="Bot Menu",
        description="Here are the available commands:",
        color=discord.Color.blue()
    )

    embed.add_field(name=".create_role [user] [role name] [color]", value="create a role", inline=False)
    embed.add_field(name=".chat [message]", value="Talk to the bot", inline=False)
    embed.add_field(name=".ping", value="Check the bot's latency", inline=False)
    embed.add_field(name=".nickname [user] [new nickname]", value="Change someone's nickname", inline=False)
    embed.add_field(name=".hello", value="Say hello to the bot", inline=False)
    embed.add_field(name=".roll", value="Roll a dice", inline=False)
    embed.add_field(name=".memberinfo", value="Get information about all members", inline=False)
    embed.add_field(name=".userinfo [user]", value="Get information about a user", inline=False)
    embed.add_field(name=".serverinfo", value="Get information about the server", inline=False)
    embed.add_field(name=".kick [user] [reason]", value="Kick someone from the server", inline=False)
    embed.add_field(name=".ban [user] [reason]", value="Ban someone from the server", inline=False)
    embed.add_field(name=".mute [user] [duration] [reason]", value="Mute someone in the server", inline=False)
    embed.add_field(name=".unmute [user]", value="Unmute a previously muted user", inline=False)
    embed.add_field(name=".delete_role [role name]", value="remove role with the same name in the server", inline=False)
    embed.add_field(name=".removerole [user] [role name]", value="remove role from someone", inline=False)
    embed.add_field(name=".addrole [user] [role name]", value="Addrole to someone", inline=False)

    await ctx.send(embed=embed)


client.run(TOKEN)
