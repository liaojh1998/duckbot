from io import BytesIO
import logging
import traceback
import sys
import re
import requests

#LRU using a segment tree, O(1) request, O(log(N)) update
#Use a hashmap to map name to loc of emoji in the tree

from discord import errors
from discord.ext import commands
from discord.ext.commands import Bot
from discord.ext.commands import Context

logger = logging.getLogger(__name__)

class EmojiChanger:
	"""Commands to manage the local 50 custom emojis and the 50 animated emojis."""
	def __init__(self, bot: Bot):
		self._bot = bot
		self._reply_to_channel = True

	def _get_dest(self, ctx: Context):
		if self._reply_to_channel:
			return ctx.message.channel
		return ctx.message.author

	async def on_command_error(self, error: Exception, ctx: Context):
		logger.info(type(error))
		error = getattr(error, 'original', error)
		ignored = (commands.CommandNotFound)
		dest = self._get_dest(ctx)
		if isinstance(error, ignored):
			logger.info(str(type(error)) + ' error has been ignored.')
		elif isinstance(error, commands.BadArgument):
			await self._bot.send_message(dest, 'Bad argument! Don\'t forget the quotes :slight_smile:.')
			await self._bot.send_message(dest, '/' + str(ctx.command) + ' ' + ctx.command.help)
		elif isinstance(error, commands.MissingRequiredArgument):
			await self._bot.send_message(dest, 'Command is missing arguments, quack.')
			await self._bot.send_message(dest, '/' + str(ctx.command) + ' ' + ctx.command.help)
		traceback.print_exception(type(error), error, error.__traceback__, file=sys.stderr)
	
	#This definitely needs to be edited
	@commands.group(pass_context=True)
	async def emoji(self, ctx: Context):
		"""Idk what im doing really"""
		if ctx.invoked_subcommand is not None:
			return
		await self._bot.say('Yikers, why did you call me?')

	@emoji.command(pass_context=True)
	async def to_pm(self, ctx: Context):
		""" -- Make Emoji Changer alert in private messages
		Usage: /emoji to_pm
		"""
		if self._reply_to_channel:
			self._reply_to_channel = False
			await self._bot.send_message(ctx.message.author, 'Shhh... Switched to private messaging mode.')
		else:
			await self._bot.send_message(ctx.message.author, 'Already switched to private messaging mode.')

	@emoji.command(pass_context=True)
	async def to_ch(self, ctx: Context):
		""" -- Make Emoji Changer alert to channel
		Usage: /emoji to_ch
		"""
		if not self._reply_to_channel:
			self._reply_to_channel = True
			await self._bot.send_message(ctx.message.channel, 'Quack, switched to channel messaging mode.')
		else:
			await self._bot.send_message(ctx.message.channel, 'Already switched to channel messaging mode.')

	@emoji.command(pass_context=True)
	async def add(self, ctx: Context, name, img_url):
		""" -- Adds an emoji to the server
		Usage: /emoji add <name> <img_url_of_emoji>
		Example: /emoji add "OSFrog" "https://static-cdn.jtvnw.net/emoticons/v1/81248/1.0"
		"""
		dest = self._get_dest(ctx)
		has = name in [emoji.name for emoji in self._bot.get_all_emojis()]
		if has:
			await self._bot.send_message(dest, 'That emoji has already been added!')
		else:
			try:
				with BytesIO(requests.get(img_url).content) as data:
					emoji = await self._bot.create_custom_emoji(server=ctx.message.server, name=name, image=data.getvalue())
				await self._bot.send_message(dest, content= \
					'Success! You have added :' + emoji.name + ': <:' + emoji.name + ':' + emoji.id + '> to the server!')
			except requests.exceptions.MissingSchema:
				await self._bot.send_message(dest, content='Don\'t forget to put http:// or https:// in front of the url.')
			except errors.InvalidArgument:
				await self._bot.send_message(dest, content='Can\'t add an emoji from an invalid image url :frowning:.')
			except:
				await self._bot.send_message(dest, content= \
					'Quack! That was an invalid command!\n' \
					'Usage: /emoji add <name> <img_url_of_emoji>\n' \
					'Example: /emoji add "OSFrog" "https://static-cdn.jtvnw.net/emoticons/v1/81248/1.0"')

	def _get_emoji(self, name):
		emoji = None
		for server_emoji in self._bot.get_all_emojis():
			if server_emoji.name == name:
				emoji = server_emoji
		return emoji

	async def _remove_emoji(self, ctx: Context, name):
		dest = self._get_dest(ctx)
		emoji = self._get_emoji(name)
		if not emoji:
			await self._bot.send_message(dest, 'Grrrr, that emoji does not exist.')
		else:
			await self._bot.delete_custom_emoji(emoji)
			await self._bot.send_message(dest, content= \
				'Removed :' + emoji.name + ': from the server!')

	@emoji.command(pass_context=True)
	async def remove(self, ctx: Context, name):
		""" -- Removes an emoji from the server
		Usage: /emoji remove <name>
		Example: /emoji remove "OSFrog"
		"""
		await self._remove_emoji(ctx, name)

	@emoji.command(pass_context=True)
	async def delete(self, ctx: Context, name):
		""" -- Same as /emoji remove
		Usage: /emoji delete <name>
		Example: /emoji delete "OSFrog"
		"""
		await self._remove_emoji(ctx, name)

	async def _rename_emoji(self, ctx: Context, current_name, new_name):
		dest = self._get_dest(ctx)
		emoji = self._get_emoji(current_name)
		if not emoji:
			await self._bot.send_message(dest, 'Quack, cannot rename a nonexistent emoji.')
		else:
			await self._bot.edit_custom_emoji(emoji=emoji, name=new_name)
			await self._bot.send_message(dest, content= \
				'Changed :' + emoji.name + ': to :' + new_name + ': <:' + emoji.name + ':' + emoji.id + '>.')

	@emoji.command(pass_context=True)
	async def rename(self, ctx: Context, current_name, new_name):
		""" -- Rename an emoji
		Usage: /emoji rename <current_name> <new_name>
		Example: /emoji edit OSFrog NewFrog
		"""
		await self._rename_emoji(ctx, current_name, new_name)

	@emoji.command(pass_context=True)
	async def edit(self, ctx: Context, current_name, new_name):
		""" -- Same as /emoji rename
		Usage: /emoji edit <current_name> <new_name>
		Example: /emoji edit OSFrog NewFrog
		"""
		await self._rename_emoji(ctx, current_name, new_name)

		#simple test on the gpg

def setup(bot: Bot):
	bot.add_cog(EmojiChanger(bot))
