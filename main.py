import discord, random, math, time, asyncio
from discord.ext.commands import has_permissions, MissingPermissions
from discord.ext import commands

#bot_token = removed for confidential reasons
prefix = '!'
bot = commands.Bot(command_prefix=prefix)
my_id = '256573011887390720'
bot_id = '712815593895624715'
link_store_channel_id = '727261208629215258'
mute_channel = None
blocked_words = []
muted_users = []
invite_links = {}
contact_staff_channels = ['🚨contact-staff', '🚨contact-mods', 'contact-mods', 'contact-staff']
channels_visible = []
channels_not_visible = []
bot.last_bumper = None
welcome_channel = None
@bot.event
async def on_ready():
    await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.listening, name="!help"))
    print('I am ready')


@bot.event
async def on_member_join(member: discord.Member):
    if member.id in muted_users:
        mute_role = discord.utils.get(member.guild.roles, name='Muted')
        for channel in member.guild.channels:
            if channel.name == 'mute-chat' or channel.name == '😶mute-chat':
                mute_channel = channel.id
            if 'welcome' in channel.name:
                welcome_channel = channel.id
        mute_channel = await bot.fetch_channel(mute_channel)
        await member.add_roles(mute_role, reason='Muted upon arrival')
        muted_users.remove(member.id)
        await mute_channel.send(f'{member.mention} ***joined the server and has been muted***')
        welcome_channel = await bot.fetch_channel(welcome_channel)
        await welcome_channel.send(f"{member.mention} ***joined the server and has been muted because the previous mute duration hasn't expired yet!***")
    if str(member.guild.id) == '689575777158561813':
        for channel in member.guild.channels:
            if channel.name == 'unverified':
                unverified_channel = channel.id
        unverified_channel = await bot.fetch_channel(unverified_channel)
        embed = discord.Embed(description=(f'Hi {member.mention}, Welcome to the G20 server. You are currently unverified. To start the process of verifying your account:\n:star: Please state your full name\n:star: Ping <@&726678750913363989> and patiently wait for a staff member to assist you'))
        embed.set_thumbnail(url=member.avatar_url)
        embed.set_footer(text=f"ID: {member.id}")
        await unverified_channel.send(member.mention, embed=embed)


@bot.command()
async def verify(ctx, member:discord.Member):
    if ctx.message.author.permissions_in(ctx.channel).manage_messages:
        if str(ctx.guild.id) != '689575777158561813':
            return
        unverified_role = discord.utils.get(member.guild.roles, name="Unverified")
        dragon_role = discord.utils.get(member.guild.roles, name="Dragons")
        if unverified_role not in member.roles:
            await ctx.send ('<a:redtick:712789179372798037> ***Member already verified***')
            return
        await member.remove_roles(unverified_role)
        await member.add_roles(dragon_role)
        await ctx.send('<a:greentick:712789179595227256> ***Member Verified***')
    else:
        await ctx.send(f'<a:redtick:712789179372798037> ***Missing Permissions!***')

@bot.event
async def on_member_remove(member):
    role = discord.utils.get(member.guild.roles, name="Muted")
    if role in member.roles:
        muted_users.append(member.id)


@bot.event
async def on_message(message):
    if message.guild is None and str(message.author.id) != bot_id:
        channel = await bot.fetch_channel(731689824532037654)
        await channel.send(f'**{message.author} ({message.author.mention}) DMed me:**\n{message.content}')
        return
    message2 = message.content.split(' ')
    for word in message2:
        for blocked_word in blocked_words:
            if blocked_word.lower() in word.lower() and str(message.author.id) != bot_id and message.content.startswith('!unblock') == False and message.author.permissions_in(message.channel).manage_messages:
                await message.delete(delay=None)
                await message.channel.send(f'{message.author.mention} ***watch your language!***', delete_after=10.0)
                print(f'{message.author} attempted to say "{message.content}" in #{message.channel.name} in {message.channel.guild}')

    if str(message.author.id) == '302050872383242240':
        bump_channel = await bot.fetch_channel('715267392279937144')
        for embed in message.embeds:
            if 'bump done' in embed.description.lower():
                await bump_channel.set_permissions(message.channel.guild.default_role, read_messages=False)
                await bump_channel.edit(name='bump-unavailable')
                bump_role = message.guild.get_role(729108411584610434)
                for member in message.guild.members:
                    if bump_role in member.roles:
                        bot.last_bumper = member
                        await bot.last_bumper.remove_roles(bump_role)
                embed_words = embed.description.split(' ')
                if embed_words[0].startswith('<@!'):
                    get_member(user_id)
                    new_bumper = message.guild.get_member(int(embed_words[0][3:-2]))
                else:
                    new_bumper = message.guild.get_member(int(embed_words[0][2:-2]))
                await new_bumper.add_roles(bump_role)
                if bump_channel.id != message.channel.id:
                    await bump_channel.send (f'***Server was bumped in {message.channel.mention}!***')
                await asyncio.sleep(7200.0)
                await bump_channel.set_permissions(message.channel.guild.default_role, send_messages=True)
                await bump_channel.edit(name ='🔔ʙᴜᴍᴘ-ᴀᴠᴀɪʟᴀʙʟᴇ🔔')
                await bump_channel.send ('***Bump Available! Type ``!d bump`` in the chat to bump the server!***')

    elif 'https://discord.gg' in message.content and message.content != invite_links[str(message.guild.id)] and str(
            message.author.id) != bot_id:
        await message.delete(delay=None)
        await message.channel.send(f"{message.author.mention} ***don't post invite links***", delete_after=10.0)
        print(
            f'{message.author} tried to send an invite link "{message.content}" in #{message.channel.name} in {message.channel.guild}')
    elif message.content.startswith('!vote'):
        await message.add_reaction('<a:greentick:712789179595227256>')
        await message.add_reaction('<a:redtick:712789179372798037>')

    if message.channel.name in contact_staff_channels and str(message.author.id) != bot_id:
        for channel in message.author.guild.channels:
            if channel.name == 'user-reports':
                report_channel = channel.id
        report_channel = await bot.fetch_channel(report_channel)
        if message.attachments == []:
            new_message = await report_channel.send(f'**<a:Siren:730518136553472091> Report from {message.author.mention} <a:Siren:730518136553472091>:**\n**Report:** {message.content}')
        else:
            # for attachment in message.attachments:
            # new_message = await report_channel.send(f'**<a:Siren:730518136553472091> Report from {message.author.mention} <a:Siren:730518136553472091>:**\n**Report:** {message.content}\n**With image(s):** {attachment.url}')
            new_message = await report_channel.send(
                f'**<a:Siren:730518136553472091> Report from {message.author.mention} <a:Siren:730518136553472091>:**\n**Report:** {message.content}\n**With image(s):**',
                files=[await i.to_file() for i in message.attachments])
        await new_message.add_reaction('<a:greentick:712789179595227256>')
        await new_message.add_reaction('<a:redtick:712789179372798037>')

        await message.delete(delay=None)


    await bot.process_commands(message)

@bot.event
async def on_reaction_add(reaction, user):
    if reaction.message.channel.name == 'user-reports':
        message_words = reaction.message.content.split(' ')
        if str(reaction.emoji) == '<a:greentick:712789179595227256>' and str(user.id) != bot_id:
            user_id = message_words[3]
            if user_id.startswith('<@!'):
                user_reported = bot.get_user(int(user_id[3:-1]))
            else:
                user_reported = bot.get_user(int(user_id[2:-1]))
            await user_reported.send(f'***Your report has been seen by a moderator in {reaction.message.guild}!***')
            await reaction.message.edit(content=f'{reaction.message.content}\n**First responder:** {user.mention}')
            await reaction.message.clear_reactions()
        elif str(reaction.emoji) == '<a:redtick:712789179372798037>' and str(user.id) != bot_id:
            await reaction.message.edit(content=f'{reaction.message.content}\n**Report discarded by:** {user.mention}')
            await reaction.message.clear_reactions()

def position(member: discord.Member = None):
    pos = sum(m.joined_at < member.joined_at for m in member.guild.members if m.joined_at is not None)
    return (pos + 1)

@bot.command(brief='Changes the nickname of the user',
             description='Changes the nickname of the user. To remove the nickname, excecute the command without entering a nickname.')
async def nick(ctx, member: discord.Member = None, *, nickname=None):
    if ctx.message.author.permissions_in(ctx.channel).manage_nicknames:
        if member == None:
            await ctx.send(f'<a:redtick:712789179372798037> ***User not defined***')
            return
        if str(member.id) == bot_id:
            await ctx.send(f'<:youtried:710714444963119165>')
            return
        try:
            await member.edit(nick=nickname)
        except:
            await ctx.send(f'<a:redtick:712789179372798037> ***Missing Permissions!***')
            return
        if nickname == None:
            await member.edit(nick=nickname)
            await ctx.send(f"<a:greentick:712789179595227256> ***{member.mention}'s nickname removed***")
        else:
            await member.edit(nick=nickname)
            await ctx.send(f"<a:greentick:712789179595227256> ***{member.mention}'s nickname changed successfully***")
    else:
        await ctx.send('<a:redtick:712789179372798037> ***Missing Permissions***')
        print(
            f"{ctx.message.author} attpempted to change {member.name}#{member.discriminator}'s nickname to {nickname} in #{ctx.channel.name} in {ctx.channel.guild}")


@bot.command(brief='Sends the invite link to this server', description='Sends the invite link to this server')
async def invite(ctx):
    if str(ctx.guild.id) in invite_links and (ctx.channel.name == 'mute-chat' or ctx.channel.name == '😶mute-chat'):
        await ctx.send('<:youtried:710714444963119165>')
    elif str(ctx.guild.id) in invite_links:
        await ctx.send(f'**Permanent invite link:** {invite_links[str(ctx.guild.id)]}')


@bot.command(brief='Gives the list of the blocked words',
             description='Gives the list of the blocked words (if the word is used in a sentence, the sentence is deleted)')
async def words(ctx):
    if ctx.message.author.permissions_in(ctx.channel).manage_messages:
        await ctx.send(f'```{blocked_words}```')
        print(f'{ctx.message.author} checked the blocked words list in #{ctx.channel} in {ctx.message.guild}')
    else:
        await ctx.send('<a:redtick:712789179372798037> ***Missing Permissions***')
        print(
            f'{ctx.message.author} attpempted to check the blocked words list in #{ctx.channel} in {ctx.message.guild}')


@bot.command(brief='Blocks the given word', description='Adds it to the blocked words list')
async def block(ctx, *, word = None):
    if ctx.message.author.permissions_in(ctx.channel).manage_messages:
        try:
            wrds = word.split(' ')
        except:
            None
        if word is None:
            await ctx.send ('<a:redtick:712789179372798037> ***Word not defined***')
            return
        elif word == '""':
            await ctx.send ("<a:redtick:712789179372798037> ***Can't block this!***")
            return
        elif len(wrds) > 1:
            await ctx.send ("<a:redtick:712789179372798037> ***Can only block one word at a time!***")
        else:
            blocked_words.append(word)
            await ctx.send('<a:greentick:712789179595227256> ***Word blocked***')
    else:
        await ctx.send('<a:redtick:712789179372798037> ***Missing Permissions***')
        print(f'{ctx.message.author} attpempted to block "{word}" in #{ctx.channel} in {ctx.message.guild}')


@bot.command(brief='Unblocks the given word', description='removes it to the blocked words list')
async def unblock(ctx, word=None):
    if ctx.message.author.permissions_in(ctx.channel).manage_messages:
        if word is None:
            await ctx.send ('<a:redtick:712789179372798037> ***Word not defined***')
        else:
            if word in blocked_words:
                blocked_words.remove(word)
                await ctx.send('<a:greentick:712789179595227256> ***Word unblocked***')
                print(f'{ctx.message.author} unblocked "{word}" in {ctx.channel} in {ctx.message.guild}')
            else:
                await ctx.send("<a:redtick:712789179372798037> ***Unable to unblock a word that wasn't blocked***")
    else:
        await ctx.send('<a:redtick:712789179372798037> ***Missing Permissions***')
        print(f'{ctx.message.author} attpempted to unblock "{word}" in #{ctx.channel} in {ctx.message.guild}')


@bot.command(brief='Shuts down the bot', description='Completely shuts down the bot')
async def logout(ctx):
    if str(ctx.author.id) == my_id:
        await ctx.send('<a:greentick:712789179595227256> ***Good Night!***')
        print('Sucessfully logged out')
        await bot.logout()
    else:
        await ctx.send('<a:redtick:712789179372798037> ***Only the bot owner can run this command***')
        print(f'{ctx.message.author} tried to run the logout command in #{ctx.channel} in {ctx.guild.name}')


@bot.command(brief='Displays the latency of the bot', description='Displays the latency of the bot in milliseconds')
async def ping(ctx):
    latency = round(bot.latency * 1000)
    await ctx.send(f'Pong! ``{latency}ms``')
    print(f'latency: {latency}ms')


@bot.command(brief='Warns the user', description='Warns the user and sends the a dm informing them')
async def warn(ctx, user: discord.User = None, *, reason=None):
    member_list = []
    for member in ctx.guild.members:
        member_list.append(member)
    if ctx.message.author.permissions_in(ctx.channel).manage_messages:
        if user == None:
            await ctx.send('<a:redtick:712789179372798037> ***User not defined***')
        elif reason == None:
            await ctx.send('<a:redtick:712789179372798037> ***Reason not defined***')
        elif user in member_list:
            await ctx.send(f'<a:greentick:712789179595227256> ***{user.name}#{user.discriminator} has been warned***')
            try:
                await user.send(f'***You have been warned in {ctx.guild.name}.*** \n ``Reason:`` \n **{reason}**')
            except:
                await ctx.send(f"<a:redtick:712789179372798037> ***Coudn't DM this user***")
            print(
                f'{user.name}#{user.discriminator} has been warned in #{ctx.channel} by {ctx.message.author} in {ctx.message.guild} for {reason}')
        else:
            await ctx.send('<a:redtick:712789179372798037> ***Invalid user***')
            print(
                f'{ctx.message.author} attpempted to warn {user.name}#{user.discriminator} in #{ctx.channel} in {ctx.message.guild} for {reason}')
    else:
        await ctx.send('<a:redtick:712789179372798037> ***Missing Permissions***')
        print(
            f'{ctx.message.author} attpempted to warn {user.name}#{user.discriminator} in #{ctx.channel} in {ctx.message.guild}')


@bot.command()
async def delete(ctx, channel, message_id):
    if ctx.message.author.permissions_in(ctx.channel).manage_messages:
        try:
            channel = await bot.fetch_channel(channel[2:-1])
        except:
            await ctx.send ('<a:redtick:712789179372798037> ***channel not defined***')
            return
        try:
            message = await channel.fetch_message(message_id)
        except:
            await ctx.send('<a:redtick:712789179372798037> ***Message not found***')
            return
        try:
            await message.delete(delay = None)
        except:
            await ctx.send('<a:redtick:712789179372798037> ***Cannot delete this message***')
            return
        await ctx.send (f'<a:greentick:712789179595227256> ***Message successfully deleted***')
    else:
        await ctx.send('<a:redtick:712789179372798037> ***Missing Permissions***')

@bot.command(brief = 'Locks the server to prevent raids', description = 'Locks the server to prevent raids (disables send messages permissions for members)')
async def lock(ctx):
    if ctx.message.author.permissions_in(ctx.channel).administrator:
        for channel in ctx.guild.text_channels:
            if channel.overwrites_for(ctx.guild.default_role).send_messages == True or channel.overwrites_for(ctx.guild.default_role).send_messages == None:
                if channel.overwrites_for(ctx.guild.default_role).read_messages == True or channel.overwrites_for(ctx.guild.default_role).read_messages == None:
                    channels_visible.append(channel)
                else:
                    channels_not_visible.append(channel)

        for channel in channels_visible:
            await channel.set_permissions(ctx.guild.default_role, send_messages=False)
            #complete_message = await ctx.send(f'**<#{channel.id}> locked**')
            #await complete_message.delete(delay=5)

        for channel in channels_not_visible:
            await channel.set_permissions(ctx.guild.default_role, read_messages=False)
        await ctx.send ('<a:greentick:712789179595227256> ***Server locked***')
    else:
        await ctx.send('<a:redtick:712789179372798037> ***Missing Permissions***')

@bot.command(brief = "Undo's the lock command",description = "Undo's the lock command")
async def unlock(ctx):
    if ctx.message.author.permissions_in(ctx.channel).administrator:
        for channel in channels_visible:
            await channel.set_permissions(ctx.guild.default_role, send_messages=None)
        for channel in channels_not_visible:
            await channel.set_permissions(ctx.guild.default_role, read_messages=False)
        channels_not_visible.clear()
        channels_visible.clear()
        await ctx.send('<a:greentick:712789179595227256> ***Server unlocked***')
    else:
        await ctx.send('<a:redtick:712789179372798037> ***Missing Permissions***')

@bot.command(brief='Mutes the user (time and reason are optional)', description='Mutes the user and sends a dm informing them. Time and reason optional parameters and time is in minutes.')
async def mute(ctx, member: discord.Member = None, *, reason = None, time = None):
    mute_channel = None
    if ctx.message.author.permissions_in(ctx.channel).manage_roles:
        if member == None:
            await ctx.send('<a:redtick:712789179372798037> ***User not defined***')
            return
        for role in member.roles:
            if role.name.lower() == 'muted':
                await ctx.send(f'<a:redtick:712789179372798037> ***{member.mention} is already muted***')
                return
        mute_role = discord.utils.get(member.guild.roles, name='Muted')
        for channel in member.guild.channels:
            if channel.name == 'mute-chat' or channel.name == '😶mute-chat':
                mute_channel = channel.id
        mute_channel = await bot.fetch_channel(mute_channel)
        words_list = ctx.message.content.split(' ')
        words_list.pop(0)
        words_list.pop(0)
        try:
            time_seconds = (float(float(words_list[-1])*60))
            if time_seconds < 300:
                await ctx.send ('<a:redtick:712789179372798037> ***Time must be atleast 5 minutes***')
                return
            words_list.pop(-1)
            if words_list == []:
                reason2 = 'Not mentioned'
            else:
                reason2 = (' '.join(words_list))
            await member.add_roles(mute_role, reason=reason2)
            await ctx.send(f'<a:greentick:712789179595227256> ***{member} has been muted***')
            try:
                await member.send(f'***You have been muted in {ctx.guild.name} for {int((time_seconds) / 60)} minutes.*** \n``Reason:`` \n **{reason2}**')
            except:
                await ctx.send(f"<a:redtick:712789179372798037> ***Couldn't DM to this user***")
            await mute_channel.send(f'{member.mention} **was muted for {int((time_seconds) / 60)} minutes.** \n **Reason:** {reason2}')
            await asyncio.sleep(int(time_seconds))
            if mute_role in member.roles:
                await member.remove_roles(mute_role, reason='Duration expired')
                await mute_channel.send(f'{member.mention} **was unmuted** \n**Reason:** Duration expired')
            else:
                return
        except Exception as e:
            print (e)
            if reason == None:
                reason = 'Not Mentioned'
            await member.add_roles(mute_role, reason=reason)
            await ctx.send(f'<a:greentick:712789179595227256> ***{member} has been muted***')
            try:
                await member.send(f'***You have been muted in {ctx.guild.name}.*** \n ``Reason:`` \n **{reason}**')
            except:
                await ctx.send(f"<a:redtick:712789179372798037> ***Couldn't send a DM to this user***")
            await mute_channel.send(f'{member.mention} **was muted** \n **Reason:** {reason}')
    else:
        await ctx.send('<a:redtick:712789179372798037> ***Missing Permissions***')
        print(f'{ctx.message.author} attpempted to mute  in #{ctx.channel} in {ctx.message.guild}')


@bot.command(brief='unmutes the user', description='unmutes the user')
async def unmute(ctx, member: discord.Member, *, reason=None):
    mute_channel = None
    role_list = []
    if ctx.message.author.permissions_in(ctx.channel).manage_roles:
        for role in member.roles:
            role_list.append(role.name.lower())
        if not 'muted' in role_list:
            await ctx.send(f'<a:redtick:712789179372798037> ***{member.mention} is already unmuted***')
            return
        mute_role = discord.utils.get(member.guild.roles, name='Muted')
        for channel in member.guild.channels:
            if channel.name == 'mute-chat' or channel.name == '😶mute-chat':
                mute_channel = channel.id
        mute_channel = await bot.fetch_channel(mute_channel)
        mute_role = discord.utils.get(member.guild.roles, name='Muted')
        await member.remove_roles(mute_role, reason=reason)
        await ctx.send(f'<a:greentick:712789179595227256> ***{member} has been unmuted***')
        await mute_channel.send(f'{member.mention} **was unmuted** \n **Reason:** {reason}')
    else:
        await ctx.send('<a:redtick:712789179372798037> ***Missing Permissions***')
        print(f'{ctx.message.author} attpempted to unmute  in #{ctx.channel} in {ctx.message.guild}')

@bot.command(brief='Sends a message in the specified channel', description='Send a message in the specified channel')
async def send(ctx, channel: discord.TextChannel, *, message):
    if ctx.message.author.permissions_in(ctx.channel).manage_messages:
        await channel.send(message)
        await ctx.send(f'<a:greentick:712789179595227256> ***Message sent in <#{channel.id}>***')
    else:
        await ctx.send('<a:redtick:712789179372798037> ***Missing Permissions***')


@bot.command(brief='Edits the message sent by the bot', description='Edits the message sent by the bot')
async def edit(ctx, channel, message_id, *, new_message):
    if ctx.message.author.permissions_in(ctx.channel).manage_messages:
        try:
            channel = await bot.fetch_channel(channel[2:-1])
        except:
            await ctx.send('<a:redtick:712789179372798037> ***channel not defined***')
            return
        try:
            message = await channel.fetch_message(message_id)
        except:
            await ctx.send('<a:redtick:712789179372798037> ***Message not found***')
            return
        try:
            await message.edit(content=new_message)
        except:
            await ctx.send('<a:redtick:712789179372798037> ***Cannot edit a message authored by another user***')
            return
        await ctx.send(f'<a:greentick:712789179595227256> ***Message successfully edited***')
    else:
        await ctx.send('<a:redtick:712789179372798037> ***Missing Permissions***')


@bot.command(brief='Returns the raw message', description='Returns the raw message')
async def raw(ctx, channel, message_id):
    if ctx.message.author.permissions_in(ctx.channel).manage_messages:
        try:
            channel = await bot.fetch_channel(channel[2:-1])
        except:
            await ctx.send('<a:redtick:712789179372798037> ***channel not defined***')
            return
        try:
            message = await channel.fetch_message(message_id)
        except:
            await ctx.send('<a:redtick:712789179372798037> ***Message not found***')
            return
        await ctx.send(f'```{prefix}edit {channel.mention} {message_id} {message.content}```')
    else:
        await ctx.send('<a:redtick:712789179372798037> ***Missing Permissions***')


@bot.command(brief='DMs the message to the specified user', description='DMs the message to the specified user')
async def dm(ctx, user: discord.User = None, *, message=None):
    member_list = []
    for member in ctx.guild.members:
        member_list.append(member)
    if ctx.message.author.permissions_in(ctx.channel).manage_messages:
        if user == None:
            await ctx.send('<a:redtick:712789179372798037> ***User not defined***')
        elif message == None:
            await ctx.send('<a:redtick:712789179372798037> ***Message not defined***')
        elif user in member_list:
            try:
                await user.send(f'**A message from {ctx.guild.name} Moderators:** \n{message}')
                await ctx.send(f'<a:greentick:712789179595227256> Sent **{message}** to {user.mention}')
                print(
                    f'''"{message}" was DM'd to {user.name}#{user.discriminator} by {ctx.message.author} in #{ctx.channel} in {ctx.message.guild}''')
            except:
                await ctx.send(f"<a:redtick:712789179372798037> ***Couldn't send a DM to this user***")
        else:
            await ctx.send("<a:redtick:712789179372798037> **Unable to DM this user**")
            print(
                f'{ctx.message.author} attpempted to DM "{message}" {user.name}#{user.discriminator} in #{ctx.channel} in {ctx.message.guild}')
    else:
        await ctx.send('<a:redtick:712789179372798037> ***Missing Permissions***')
        print(
            f'{ctx.message.author} attpempted to DM "{message}" {user.name}#{user.discriminator} in #{ctx.channel} in {ctx.message.guild}')
    member_list = []


@bot.command(brief='Deletes a specified amount of messages',
             description='Deleted a specified amout of messages in the channel the command is executed in')
async def purge(ctx, amount=None):
    if ctx.message.author.permissions_in(ctx.channel).manage_messages:
        if amount == None:
            await ctx.send('<a:redtick:712789179372798037> ***Amount missing***')
            print(
                f'{ctx.message.author} attpempted to purge messages (no amount given) in #{ctx.channel} in {ctx.message.guild}')
        elif type(int(amount)) != int:
            await ctx.send('<a:redtick:712789179372798037> ***Input a positive integer***')
            print(
                f'{ctx.message.author} attpempted to purge messages (no amount given) in #{ctx.channel} in {ctx.message.guild}')
        elif int(amount) <= 0:
            await ctx.send('<a:redtick:712789179372798037> ***Input a positive integer***')
            print(
                f'{ctx.message.author} attpempted to purge {amount} messages in #{ctx.channel} in {ctx.message.guild}')
        else:
            if int(amount) >= 100:
                amount = 100
            await ctx.channel.purge(limit=(int(amount) + 1))
            # await ctx.send(f"<a:greentick:712789179595227256> ***{amount} message(s) have been purged***",delete_after=10.0)
            print(f"Purged {amount} messages by {ctx.message.author} in #{ctx.channel} in {ctx.guild.name}")

    else:
        await ctx.send('<a:redtick:712789179372798037> ***Missing Permissions***')
        print(f'{ctx.message.author} attpempted to purge {amount} messages in #{ctx.channel} in {ctx.message.guild}')


@bot.command(brief='Kicks the user out of the server',
             description='Kicks the user out of the server informing them the reason via a DM')
async def kick(ctx, member: discord.Member, *, reason=None):
    if ctx.message.author.permissions_in(ctx.channel).kick_members:
        if member != ctx.author:
            if not member.permissions_in(ctx.channel).administrator:
                await member.kick(reason=reason)
                await ctx.send(f'<a:greentick:712789179595227256> {member.mention} ***has been kicked***')
                await member.send(f'***You have been kicked from {ctx.guild.name}.*** \n``Reason:`` \n**{reason}**')
            else:
                await ctx.send(f"<a:redtick:712789179372798037> ***Can't kick this user!***")
        else:
            await ctx.send(f"<a:redtick:712789179372798037> ***You can't kick yourself!***")
    else:
        await ctx.send('<a:redtick:712789179372798037> ***Missing Permissions***')


'''
@bot.command(brief='Bans the user from the server',
             description='Bans the user from the server informing them the reason via DM')
async def ban(ctx, user:discord.User = None, *, reason=None):
    if ctx.message.author.permissions_in(ctx.channel).administrator:
        if ctx.message.author == user:
            await ctx.send(f"<a:redtick:712789179372798037> ***You can't ban yourself***")
            return
        if user in ctx.guild.members:
            user_id = int(user.id)
            user = await ctx.guild.get_member(user_id)
            if user.permissions_in(ctx.channel).administrator:
                await ctx.send(f"<a:redtick:712789179372798037> ***Can't ban this user!***")
                return
            else:
                try:
                    await user.send(f'***You have been banned from {ctx.guild.name}.***\n``Reason:``\n **{reason}**')
                except:
                    await ctx.send("<a:redtick:712789179372798037> **Unable to DM this user**")
                await user.ban(reason=reason, delete_message_days=0)
                await ctx.send(f'<a:greentick:712789179595227256> ***{member.mention} has been banned***')

'''

@bot.command(brief='Bans the user from the server',
             description='Bans the user from the server informing them the reason via DM')
async def ban(ctx, member:discord.User, *, reason=None):
    if ctx.message.author.permissions_in(ctx.channel).administrator:
        if member != ctx.author:
            if not member.permissions_in(ctx.channel).administrator:
                if member is None:
                    await ctx.send('<a:redtick:712789179372798037> ***User not defined***')
                    return
                else:
                    try:
                        await member.ban(reason=reason, delete_message_days = 0)
                        await ctx.send(f'<a:greentick:712789179595227256> {member.mention} ***has been banned***')
                    except:
                        await ctx.send (f'<a:redtick:712789179372798037> ***Invalid user***')
                try:
                    await member.send(f'***You have been banned from {ctx.guild.name}.*** \n``Reason:``\n **{reason}**')
                except:
                    await ctx.send ("<a:redtick:712789179372798037> **Unable to DM this user**")
            else:
                await ctx.send(f"<a:redtick:712789179372798037> ***Can't ban this user!***")
        else:
            await ctx.send(f"<a:redtick:712789179372798037> ***You can't ban yourself!***")

    else:
        await ctx.send('<a:redtick:712789179372798037> ***Missing Permissions***')



@bot.command(brief='Unbans the user from the server',
             description='Unbans the user from the server informing them the reason via DM')
async def unban(ctx, id: int):
    if ctx.message.author.permissions_in(ctx.channel).administrator:
        user = await bot.fetch_user(id)
        await ctx.guild.unban(user)
        await ctx.send(f'<a:greentick:712789179595227256> {user.mention} ***has been unbanned***')
    else:
        await ctx.send('<a:redtick:712789179372798037> ***Missing Permissions***')

@bot.command()
async def banned(ctx):
    if ctx.message.author.permissions_in(ctx.channel).administrator:
        banned_users = await ctx.message.guild.bans()
        if banned_users == []:
            await ctx.send('***<a:redtick:712789179372798037> No user is banned***')
        else:
            for banned_user in banned_users:
                await ctx.send(
                    f'***{banned_user.user.name}#{banned_user.user.discriminator} ({banned_user.user.mention}) was banned for*** **: {banned_user.reason}**\n')
    else:
        await ctx.send('<a:redtick:712789179372798037> ***Missing Permissions***')

''' 
# Setting `Playing ` status
await bot.change_presence(activity=discord.Game(name="a game"))
# Setting `Streaming ` status
await bot.change_presence(activity=discord.Streaming(name="My Stream", url=my_twitch_url))
# Setting `Listening ` status
await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.listening, name="a song"))
# Setting `Watching ` status
await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name="a movie"))
'''

'''
@bot.command()
async def embed(ctx):
    embed = discord.Embed(title='Title',
                          description='This is a description')
    embed.set_footer(text='This is a footer')
    embed.set_image(url='https://cdn.discordapp.com/emojis/719787536976969800.png?v=1')
    embed.set_thumbnail(url='https://cdn.discordapp.com/emojis/719787536976969800.png?v=1')
    embed.set_author(name='Author Name', icon_url='https://cdn.discordapp.com/emojis/719787536976969800.png?v=1')
    embed.add_field(name='field name', value='field value',inline=False)
    await ctx.send (embed=embed)
'''

@bot.command()
async def avatar(ctx, member: discord.Member = None):
    if member is None:
        member = ctx.message.author
    role_for_color = []
    for role in member.roles:
        if role != ctx.guild.default_role:
            role_for_color.append(role)
    role_for_color.reverse()
    if str(member.top_role.colour) == '#000000' and len(role_for_color) > 1:
        top_role = role_for_color[1]
    else:
        top_role = member.top_role
    top_role_color = top_role.colour
    embed = discord.Embed(colour=top_role_color, title=f"{member}'s Avatar:")
    embed.set_image(url=member.avatar_url)
    await ctx.send (embed=embed)

@bot.command(aliases=['check', 'whois', 'stats'])
async def userinfo(ctx, member: discord.Member = None):
    if member is None:
        member = ctx.message.author
    roles_list = []
    role_for_color = []
    for role in member.roles:
        if role != ctx.guild.default_role:
            roles_list.append(role.mention)
    roles_list.reverse()
    roles = (' '.join(roles_list))
    pos = position(member)
    for role in member.roles:
        role_for_color.append(role)
    role_for_color.reverse()
    if str(member.top_role.colour) == '#000000' and len(roles_list) > 1:
        top_role = role_for_color[1]
    else:
        top_role = member.top_role
    top_role_color = top_role.colour
    if roles_list == []:
        embed = discord.Embed(description=member.mention)
    else:
        if str(top_role_color) == '#000000':
            embed = discord.Embed(description= member.mention)
        else:
            embed = discord.Embed(colour= top_role_color, description=member.mention)
    embed.set_thumbnail(url=member.avatar_url)
    embed.set_author(name=f"User Info - {member}", icon_url=member.avatar_url)
    embed.add_field(name="Display Name:", value=member.display_name, inline=False)
    embed.add_field(name="Account Registered On:", value=member.created_at.strftime("%#d %B %Y, %I:%M %p UTC"), inline=True)
    embed.add_field(name="Joined Server On:", value=member.joined_at.strftime("%#d %B %Y, %I:%M %p UTC"), inline=True)
    embed.add_field(name='Join Position:', value=pos, inline=False)
    embed.add_field(name = 'User ID:', value=member.id, inline=False)
    if roles_list == []:
        embed.add_field(name=f'Role(s): [{len(roles_list)}]', value= 'No Roles')
    else:
        embed.add_field(name=f'Role(s): [{len(roles_list)}]', value=roles)
    key_permissions = []
    if member.permissions_in(ctx.channel).administrator:
        key_permissions.append('``Administrator``')
    if member.permissions_in(ctx.channel).mention_everyone:
        key_permissions.append('``Mention @everyone``')
    if member.permissions_in(ctx.channel).kick_members:
        key_permissions.append('``Kick Members``')
    if member.permissions_in(ctx.channel).ban_members:
        key_permissions.append('``Ban Members``')
    if member.permissions_in(ctx.channel).manage_channels:
        key_permissions.append('``Manage Channels``')
    if member.permissions_in(ctx.channel).manage_messages:
        key_permissions.append('``Mute Members``')
        key_permissions.append('``Warn Members``')
        key_permissions.append('``Manage Messages``')
    if member.permissions_in(ctx.channel).manage_roles:
        key_permissions.append('``Manage Roles``')
    if member.permissions_in(ctx.channel).manage_emojis:
        key_permissions.append('``Manage Emojis``')

    if key_permissions == []:
        pass
    else:
        key_permissions = (' '.join(key_permissions))
        embed.add_field(name=f'Key Permissions:', value=key_permissions, inline=False)

    embed.set_footer(text=f"Requested by {ctx.author}")

    await ctx.send(embed=embed)

@bot.command()
async def members(ctx, *, role:discord.Role = None):
    if role is None:
        await ctx.send ('<a:redtick:712789179372798037> ***Role not defined!***')
        return
    members = []
    for member in ctx.guild.members:
        for role1 in member.roles:
            if role1.name.lower() == role.name.lower():
                members.append(member.mention)
    if members == []:
        embed3 = discord.Embed(title=('Currently no members have this role'), colour=role.colour)
        embed3.set_footer(text=f"Requested by {ctx.author}")
        await ctx.send(embed=embed3)
        return
    members1 = (' '.join(members))
    embed = discord.Embed(title= (f'Members in {role.name} (Total: {len(members)}):'), colour=role.colour, description=members1)
    embed.set_footer(text=f"Requested by {ctx.author}")
    if len(embed.description) + len(embed.title) < 2048:
        await ctx.send(embed=embed)
    else:
        embed2 = discord.Embed(title= (f'Number of Members in {role.name}: {len(members)}'), colour=role.colour, description = "Too many members to list")
        embed2.set_footer(text=f"Requested by {ctx.author}")
        await ctx.send(embed=embed2)

@bot.command(aliases=['rate', 'slowmode'], brief = 'Set the slowmode cooldown of a channel', description = 'Set the slowmode cooldown of a channel')
async def cooldown(ctx, cooldown_time = None):
    if ctx.message.author.permissions_in(ctx.channel).manage_channels:
        if cooldown_time != None:
            try:
                int(cooldown_time)
            except:
                await ctx.send(f"<a:redtick:712789179372798037> ***Time not mentioned***")
                return
            if int(cooldown_time) > 21600:
                await ctx.send (f"<a:redtick:712789179372798037> ***Can't be longer than 6 hours***")
                return
            await ctx.channel.edit(slowmode_delay=int(cooldown_time))
            await ctx.send (f'<a:greentick:712789179595227256> ***Slowmode cooldown Time set to {cooldown_time} second(s)***')
            return
        else:
            await ctx.send(f'**Current slowmode cooldown time: {ctx.channel.slowmode_delay} second(s)**')
    else:
        await ctx.send('<a:redtick:712789179372798037> ***Missing Permissions***')

bot.run(bot_token)
