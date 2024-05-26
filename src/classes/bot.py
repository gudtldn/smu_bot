import discord
from discord.ext import commands

import os
import logging

from src.classes.course_modal import CourseModal


class Bot(commands.Bot):
    def __init__(self):
        self.logger = logging.getLogger("discord.classes.Bot")

        intents = discord.Intents.default()
        intents.message_content = True

        super().__init__(
            command_prefix="__",
            intents=intents,
            help_command=None,
        )

    async def setup_hook(self):
        for file in os.listdir("src/cogs"):
            if file.startswith("_"):
                continue

            if os.path.isdir(f"./src/cogs/{file}") and "__init__.py" in os.listdir(f"./src/cogs/{file}"):
                await self.load_extension(f"src.cogs.{file}")
            elif file.endswith(".py"):
                await self.load_extension(f"src.cogs.{file[:-3]}")

        await self.tree.sync()

    async def on_ready(self):
        self.logger.info(f"Logged in as {self.user}")

        # 강좌 신청하기 메시지 생성
        channel: discord.TextChannel = self.get_channel(1244194576189620275)

        last_message = None
        async for message in channel.history(limit=1):
            last_message = message

        if last_message is not None and last_message.author == self.user:
            await last_message.delete()

        embed = discord.Embed(
            title="강좌 신청하기",
            description="강좌 신청을 하려면 아래 버튼을 눌러주세요.",
            color=discord.Color.blue()
        )
        view = discord.ui.View(timeout=None)
        button = discord.ui.Button(label="신청하기", style=discord.ButtonStyle.primary)
        button.callback = lambda interaction: interaction.response.send_modal(CourseModal())
        view.add_item(button)

        await channel.send(embed=embed, view=view)

    async def on_message(self, message: discord.Message):
        if message.author.bot:
            return
        await self.process_commands(message)

    async def on_command_error(self, ctx: commands.Context["Bot"], error: commands.CommandError):
        if isinstance(error, commands.CommandNotFound):
            return

        if ctx.command_failed:
            await ctx.reply("오류가 발생했습니다.")
            self.logger.error("Ignoring exception in command %s", ctx.command, exc_info=error)


class Cog(commands.Cog):
    def __init__(self, bot: Bot):
        self.bot = bot
        self.logger = logging.getLogger(f"discord.cog.{self.__class__.__name__}")

        self.bot.logger.debug(f"Cog {self.__class__.__name__} loaded")

    # 명령어가 실행되기 전 실행되는 함수
    async def cog_before_invoke(self, ctx: commands.Context[Bot]):
        pass
