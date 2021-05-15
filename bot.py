#!/usr/bin/env python
"""
2020-11-05
started from:
https://realpython.com/how-to-make-a-discord-bot-python/

https://discordpy.readthedocs.io/en/latest/faq.html
this page explains why await bot.process_commands(message) is
necessary in on_message, and also explains how to make subcommands.

"""
import os
from discord.ext import commands

from price_check import search_card

env = dict()
with open('env.txt', 'r') as fr:
    for line in fr:
        line = line.strip()
        if line.startswith('#'):
            continue
        if '=' not in line:
            continue
        k, v = line.split('=', 1)
        env[k] = v

TOKEN = env.get('DISCORD_TOKEN')
owner_user_id = int(env.get('owner_user_id'))


# client = discord.Client()
bot = commands.Bot(command_prefix='!')

async def get_owner():
    try:
        return get_owner.owner
    except AttributeError:
        print(f'owner_user_id: {owner_user_id}')
        setattr(get_owner, 'owner', await bot.fetch_user(owner_user_id))
        return get_owner.owner


async def authorized(ctx):
    if ctx.author.id == owner_user_id:
        return True
    await ctx.send(f'you are unauthorized to run this command')
    print(
        f'user @{ctx.author.name}#{ctx.author.discriminator} '
        f'({ctx.author.id}) tried to run: {ctx.message.content}'
    )
    owner = await get_owner()
    await owner.send(
        f'unauthorized user <@!{ctx.author.id}> '
        f'tried to run: {ctx.message.content}'
    )
    return False


@bot.event
async def on_ready():
    print(f'{bot.user} has connected to Discord!')

    owner = await get_owner()
    await owner.send(f'hello!!!!! up and running!!!!!!')


@bot.event
async def on_message(message):
    '''
    allows us to view and process every message the bot can see
    '''
    if message.author == bot.user:
        return

    # the new versions of discord.py require this to
    # be able to run normal commands in addition to
    # viewing all messsages
    await bot.process_commands(message)


class Commands(commands.Cog):

    @commands.command(aliases=['find', 'lookup', 'card'])
    async def search(self, ctx, *args):
        """search for card by name"""
        if not args:
            await ctx.send("please include the name of the card, e.g. `!search doubling season`")
            return
        card_title = ' '.join(args)
        results = search_card(card_title)
        message = '\n'.join(results)
        await ctx.send(message)


class Admin(commands.Cog):
    'commands for authorized administrators only'

    @commands.command()
    async def debug(self, ctx):
        'open a terminal debug'
        if not await authorized(ctx):
            return
        try:
            import readline
        except ImportError:
            print("failed to import readline for pdb/ipdb debugging")
        try:
            import ipdb as pdb
        except ImportError:
            import pdb
        pdb.set_trace()
        await ctx.send(f'done debugging')

    @commands.command(aliases=['rs'])
    async def restart(self, ctx):
        'restart the bot'
        if not await authorized(ctx):
            return

        await ctx.send('restarting...')
        os.system('./bot.py')


class Utilities(commands.Cog):
    @commands.command()
    async def suggest(self, ctx):
        'make a suggestion to the bot creator'
        await bot.wait_until_ready()
        owner = await get_owner()
        await owner.send(
            f'user <@!{ctx.author.id}> says: {ctx.message.content}'
        )


if __name__ == '__main__':
    bot.add_cog(Admin(bot))
    bot.add_cog(Utilities(bot))
    bot.add_cog(Commands(bot))
    bot.run(TOKEN)
