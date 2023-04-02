import discord
import time
import globals
from typing import Optional
from discord.ext import commands
from chain import ConversationCache, chat


class Context(commands.Cog):
    def __init__(self, bot) -> None:
        self.bot = bot


    @commands.slash_command(description="Set the context for Bloom or show it")
    async def context(self, ctx: discord.ApplicationContext, text: Optional[str] = None):
        """
        This function directs the user to the appropriate activity to engage in with the text they provided.
        """
        LOCAL_CHAIN = globals.CACHE.get(ctx.channel_id)
        if text is None:
            # no text given, show current text to user or let them know nothing's been set
            if LOCAL_CHAIN is not None and LOCAL_CHAIN.context is not None:
                await ctx.respond(f"*Current context:* {LOCAL_CHAIN.context}", ephemeral=True)
            else:
                await ctx.respond(f"*Bloom never got any text! Paste some text after the* `/context` *command*")
        else:
            # text given, assign or update the context
            if LOCAL_CHAIN is not None and LOCAL_CHAIN.context is not None:
                start = time.time()
                await ctx.response.defer()
                # updating the context, so restart conversation
                await ctx.invoke(self.bot.get_command('restart'), respond=False)
                await ctx.respond("What would you like to do with the text you provided?", view=ContextView(text))
                end = time.time()
                print(f"Elapsed: {end - start}")
            else:
                # setting context for the first time
                await ctx.response.defer()
                start = time.time()
                await ctx.respond("What would you like to do with the text you provided?", view=ContextView(text))
                end = time.time()
                print(f"Elapsed: {end - start}")


    @commands.slash_command(name="discuss", description="Discuss your text with Bloom")
    async def discuss(self, ctx: discord.ApplicationContext, text: Optional[str] = None):
        LOCAL_CHAIN = globals.CACHE.get(ctx.channel_id)
        if text is None:
            # no text given, show current text to user or let them know nothing's been set
            if LOCAL_CHAIN is not None and LOCAL_CHAIN.context is not None:
                await ctx.respond(f"*Currently discussing:* {LOCAL_CHAIN.context}", ephemeral=True)
            else:
                await ctx.respond(f"*Bloom doesn't have anything to discuss! Paste some text after the* `/discuss` *command*")
        else:
            # text given, assign or update the context
            if LOCAL_CHAIN is not None and LOCAL_CHAIN.context is not None:
                start = time.time()
                await ctx.response.defer()
                # updating the context, so restart conversation
                await ctx.invoke(self.bot.get_command('restart'), respond=False)
                LOCAL_CHAIN.context = text
                print(f"*Discussion updated to:* {LOCAL_CHAIN.context}")
                response = await chat(
                    context=LOCAL_CHAIN.context,
                    starter_chain=globals.STARTER_CHAIN
                )
                LOCAL_CHAIN.response_memory.chat_memory.add_ai_message(response)
                await ctx.followup.send(response)
                end = time.time()
                print(f"Elapsed: {end - start}")
            else:
                # setting context for the first time
                start = time.time()
                await ctx.response.defer()
                # Create new cache entry
                LOCAL_CHAIN = ConversationCache(text)
                globals.CACHE.put(ctx.channel_id, LOCAL_CHAIN)
                print(f"*Discussion set to:* {LOCAL_CHAIN.context}")
                response = await chat(
                    context=text,
                    starter_chain=globals.STARTER_CHAIN
                )
                LOCAL_CHAIN.response_memory.chat_memory.add_ai_message(response)
                await ctx.followup.send(response)
                end = time.time()
                print(f"Elapsed: {end - start}")


    @commands.slash_command(name="workshop", description="Workshop your writing with Bloom")
    async def workshop(self, ctx: discord.ApplicationContext, text: Optional[str] = None):
        LOCAL_CHAIN = globals.CACHE.get(ctx.channel_id)
        if text is None:
            # no text given, show current text to user or let them know nothing's been set
            if LOCAL_CHAIN is not None and LOCAL_CHAIN.context is not None:
                await ctx.respond(f"*Currently workshopping:* {LOCAL_CHAIN.context}", ephemeral=True)
            else:
                await ctx.respond(f"*Bloom doesn't have anything to workshop! Paste some text after the* `/workshop` *command*")
        else:
            # text given, assign or update the context
            if LOCAL_CHAIN is not None and LOCAL_CHAIN.context is not None:
                start = time.time()
                await ctx.response.defer()
                # updating the context, so restart conversation
                await ctx.invoke(self.bot.get_command('restart'), respond=False)
                LOCAL_CHAIN.context = text
                print(f"*Workshop text updated to:* {LOCAL_CHAIN.context}")
                response = await chat(
                    context=LOCAL_CHAIN.context,
                    starter_chain=globals.STARTER_CHAIN
                )
                LOCAL_CHAIN.response_memory.chat_memory.add_ai_message(response)
                await ctx.followup.send(response)
                end = time.time()
                print(f"Elapsed: {end - start}")
            else:
                # setting context for the first time
                start = time.time()
                await ctx.response.defer()
                # Create new cache entry
                LOCAL_CHAIN = ConversationCache(text)
                globals.CACHE.put(ctx.channel_id, LOCAL_CHAIN)
                print(f"*Workshop text set to:* {LOCAL_CHAIN.context}")
                response = await chat(
                    context=text,
                    starter_chain=globals.STARTER_CHAIN
                )
                LOCAL_CHAIN.response_memory.chat_memory.add_ai_message(response)
                await ctx.followup.send(response)
                end = time.time()
                print(f"Elapsed: {end - start}")


class ContextView(discord.ui.View):
    def __init__(self, text):
        super().__init__()
        self.text=text

    @discord.ui.button(label="Discuss", style=discord.ButtonStyle.primary, emoji="💬")
    async def discuss_button_callback(self, button, interaction):
        start = time.time()
        await interaction.response.defer()

        self.discuss_button_callback.disabled = True
        self.workshop_button_callback.disabled = True

        # edit the message's view ASAP so people can't click multiple times before it responds
        await interaction.followup.edit_message(interaction.message.id, view=self) 

        async with interaction.channel.typing():
            # Create new cache entry
            LOCAL_CHAIN = ConversationCache(self.text)
            globals.CACHE.put(interaction.channel_id, LOCAL_CHAIN)
            print(f"Context set to: {LOCAL_CHAIN.context}")
            response = await chat(
                context=self.text,
                starter_chain=globals.STARTER_CHAIN
            )
            LOCAL_CHAIN.response_memory.chat_memory.add_ai_message(response)
            await interaction.followup.send(response)
        
        end = time.time()
        print(f"Elapsed: {end - start}")


    @discord.ui.button(label="Workshop", style=discord.ButtonStyle.primary, emoji="✍️")
    async def workshop_button_callback(self, button, interaction):
        start = time.time()
        await interaction.response.defer()

        self.discuss_button_callback.disabled = True
        self.workshop_button_callback.disabled = True
        
        # edit the message's view ASAP so people can't click multiple times before it responds
        await interaction.followup.edit_message(interaction.message.id, view=self)

        async with interaction.channel.typing():
            # Create new cache entry
            LOCAL_CHAIN = ConversationCache(self.text)
            globals.CACHE.put(interaction.channel_id, LOCAL_CHAIN)
            print(f"Context set to: {LOCAL_CHAIN.context}")
            response = await chat(
                context=self.text,
                starter_chain=globals.STARTER_CHAIN
            )
            LOCAL_CHAIN.response_memory.chat_memory.add_ai_message(response)
            await interaction.followup.send(response)
        
        end = time.time()
        print(f"Elapsed: {end - start}")


def setup(bot):
    bot.add_cog(Context(bot))