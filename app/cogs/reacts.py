import logging
import re

from discord import Message
from discord.ext.commands import Bot

logger = logging.getLogger(__name__)


class Reacts:
    def __init__(self, bot: Bot):
        self.bot = bot

        @bot.listen('on_message')
        async def f(message: Message):
            if message.author == bot.user:
                return

            if re.search(r'\bcloud9\b', message.content.lower()):
                await bot.add_reaction(message, '🇫')

        @bot.listen('on_message')
        async def sadboys(message: Message):
            if message.author == bot.user:
                return

            if re.search(r'\beg\b', message.content.lower()):
                await bot.add_reaction(message, '🇸')
                await bot.add_reaction(message, '🇦')
                await bot.add_reaction(message, '🇩')
                await bot.add_reaction(message, '🇧')
                await bot.add_reaction(message, '🇴')
                await bot.add_reaction(message, '🇾')
                await bot.add_reaction(message, '🇿')


def setup(bot: Bot):
    bot.add_cog(Reacts(bot))
