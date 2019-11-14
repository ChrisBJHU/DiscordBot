import asyncio
import os
import subprocess
import sys
import time
import traceback
import aiohttp
import xlrd
from utils.logger import log

log.init()

from utils.bootstrap import Bootstrap

Bootstrap.run_checks()

from utils import checks
from utils.language import Language

from discord.ext import commands
from utils.config import Config
from utils.tools import *
from utils.channel_logger import Channel_Logger
from utils.mysql import *
from utils.buildinfo import *

config = Config()
log.setupRotator(config.log_date_format, config.log_time_format)
if config.debug:
    log.enableDebugging()  # pls no flame
bot = commands.AutoShardedBot(command_prefix=config.command_prefix,
                              description="A discordbot generated by Chrono#2050", pm_help=None)
channel_logger = Channel_Logger(bot)
aiosession = aiohttp.ClientSession(loop=bot.loop)
lock_status = config.lock_status

extensions = [
    "commands.fun",
]

# Thy changelog
change_log = [
]


async def _restart_bot():
    try:
        await aiosession.close()
        await bot.cogs["Music"].disconnect_all_voice_clients()
    except:
        pass
    await bot.logout()
    subprocess.call([sys.executable, "bot.py"])


async def _shutdown_bot():
    try:
        aiosession.close()
        await bot.cogs["Music"].disconnect_all_voice_clients()
    except:
        pass
    await bot.logout()


async def set_default_status():
    if not config.enable_default_status:
        return
    type = config.default_status_type
    name = config.default_status_name
    try:
        type = discord.Status(type)
    except:
        type = discord.Status.online
    if name is not None:
        if config.default_status_type == "stream":
            if config.default_status_name is None:
                log.critical("If the status type is set to \"stream\" then the default status game must be specified")
                os._exit(1)
            status = discord.Activity(name=name, url="",
                                      type=discord.ActivityType.streaming)
        else:
            status = discord.Activity(name=name, type=discord.ActivityType.playing)
        await bot.change_presence(status=type, activity=status)
    else:
        await bot.change_presence(status=type)


@bot.event
async def on_resumed():
    log.info("Reconnected to discord!")


@bot.event
async def on_ready():
    print('Logged in as')
    print(bot.user.name)
    print(bot.user.id)
    print('------')
    log.debug("Debugging enabled!")

    for extension in extensions:
        try:
            bot.load_extension(extension)
        except Exception as e:
            log.error("Failed to load extension {}\n{}: {}".format(extension, type(e).__name__, e))


@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        return
    if isinstance(error, commands.DisabledCommand):
        await ctx.send(Language.get("bot.errors.disabled_command", ctx))
        return
    if isinstance(error, checks.owner_only):
        await ctx.send(Language.get("bot.errors.owner_only", ctx))
        return
    if isinstance(error, checks.dev_only):
        await ctx.send(Language.get("bot.errors.dev_only", ctx))
        return
    if isinstance(error, checks.support_only):
        await ctx.send(Language.get("bot.errors.support_only", ctx))
        return
    if isinstance(error, checks.not_nsfw_channel):
        await ctx.send(Language.get("bot.errors.not_nsfw_channel", ctx))
        return
    if isinstance(error, checks.not_guild_owner):
        await ctx.send(Language.get("bot.errors.not_guild_owner", ctx))
        return
    if isinstance(error, checks.no_permission):
        await ctx.send(Language.get("bot.errors.no_permission", ctx))
        return
    if isinstance(error, commands.NoPrivateMessage):
        await ctx.send(Language.get("bot.errors.no_private_message", ctx))
        return
    if isinstance(ctx.channel, discord.DMChannel):
        await ctx.send(Language.get("bot.errors.command_error_dm_channel", ctx))
        return

    # In case the bot failed to send a message to the channel, the try except pass statement is to prevent another error
    try:
        await ctx.send(Language.get("bot.errors.command_error", ctx).format(error))
    except:
        pass
    log.error("An error occured while executing the {} command: {}".format(ctx.command.qualified_name, error))


@bot.before_invoke
async def on_command_preprocess(ctx):
    if isinstance(ctx.channel, discord.DMChannel):
        guild = "Private Message"
    else:
        guild = "{}/{}".format(ctx.guild.id, ctx.guild.name)
    log.info("[Command] [{}] [{}/{}]: {}".format(guild, ctx.author.id, ctx.author, ctx.message.content))



@bot.command()
async def joinserver(ctx):
    """Sends the bot's OAuth2 link"""
    await ctx.author.send(Language.get("bot.joinserver", ctx).format(
        "https://discordapp.com/oauth2/authorize?client_id=593065241311707148&scope=bot&permissions=0"))

print("Connecting...")
bot.run(config._token)
