import discord
from discord.ext import commands

import os
import dotenv
import logging
from logging.handlers import TimedRotatingFileHandler

from src.classes.bot import Bot

dotenv.load_dotenv() # .env 파일 로드


# 파일 로그 설정
file_handler = TimedRotatingFileHandler(
    filename=f"./logs/latest.log",
    when="midnight",
    interval=1,
    backupCount=30,
    encoding="utf-8"
)
file_handler.setFormatter(
    logging.Formatter(
        fmt="[{asctime}] {levelname:<8} <{name}> [{funcName} | {lineno}] >> {message}",
        datefmt="%Y-%m-%d %H:%M:%S",
        style="{"
    )
)
file_handler.setLevel(logging.DEBUG)
logging.getLogger().addHandler(file_handler)


bot = Bot()

@bot.command(
    name="reload",
)
@commands.is_owner()
async def reload_cog(ctx: commands.Context):
    await ctx.defer(ephemeral=True)

    for filename in os.listdir("./src/cogs"):
        if filename.startswith("_"):
            continue

        cog_name = None
        if os.path.isdir(f"./src/cogs/{filename}") and "__init__.py" in os.listdir(f"./src/cogs/{filename}"):
            cog_name = filename
        elif filename.endswith(".py"):
            cog_name = filename[:-3]

        await bot.reload_extension(f"src.cogs.{cog_name}")
        bot.logger.info(f"리로드 완료: src.cogs.{cog_name}")

    await ctx.send("리로드 완료", ephemeral=True)

@reload_cog.error
async def reload_cog_error(interaction: discord.Interaction, error: commands.CommandError):
    if isinstance(error, commands.NotOwner):
        interaction.command_failed = False

bot.run(
    token=os.getenv("DISCORD_BOT_TOKEN"),
    log_level=logging.INFO
)
