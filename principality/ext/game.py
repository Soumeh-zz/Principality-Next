from nextcord import Member, Interaction, Embed, SlashApplicationCommand
from cog import Cog

class Game():

    def __init__(self):
        self.started = False
        self.players = []

class GameCog(Cog):

    def __init__(self, *args, **kwargs):

        super().__init__(*args, **kwargs)

        if not hasattr(self, 'game_name'): self.game_name = 'sample_game'
        if not hasattr(self, 'game_max_players'): self.game_max_players = 0
        if not hasattr(self, 'game_can_join_after_start'): self.game_can_join_after_start = False

        @Cog.slash_command(self.game_name, guild_ids=[802577295960571907])
        async def game(self, ctx: Interaction):
            pass

        # lobby
        @game.subcommand()
        async def lobby(self, ctx: Interaction):
            game = self.games.get(ctx.channel.id, None)
            if not game: return await ctx.send("There isn't a game in this channel!")
            await ctx.send(self.games.get(ctx.channel.id, 'None'))

        # joining
        @game.subcommand()
        async def join(self, ctx: Interaction):

            # make a new game instance if it doesn't exist
            if ctx.channel.id not in self.games:
                self.games[ctx.channel.id] = Game()
            game = self.games[ctx.channel.id]

            # check if the player is already in the lobby
            player = ctx.user
            if player in game.players:
                return await ctx.send("You already joined the lobby!", ephemeral=True)

            # check if there's space
            if self.game_max_players and self.game_max_players >= len(game.players):
                return await ctx.send("The lobby is already full!", ephemeral=True)

            # check if the player is already in the lobby
            if player in game.players:
                return await ctx.send("You already joined the lobby!", ephemeral=True)

            game.players.append(player)

        # starting
        @game.subcommand()
        async def start(self):
            game = self.games.get(ctx.channel.id, None)
            if not game: return await ctx.send("There isn't a game in this channel!")
            pass

        @game.subcommand()
        async def begin(self):
            await self.start()

        # quitting
        @game.subcommand()
        async def quit(self, ctx: Interaction):
            game = self.games.get(ctx.channel.id, None)
            if not game: return await ctx.send("There isn't a game in this channel!")
            player = ctx.user
            if player not in game.players:
                return await ctx.send("You aren't in the game!", ephemeral=True)
            await self.send(embed=Embed(description=f"{player.mention} has left the game!"))
            self.players.remove(player)

        @game.subcommand()
        async def leave(self, ctx: Interaction):
            await self.quit(ctx)
        
        # stop
        @game.subcommand()
        async def stop(self, ctx: Interaction):
            game = self.games.get(ctx.channel.id, None)
            if not game: return await ctx.send("There isn't a game in this channel!")
            player = ctx.user
            if player not in game.players:
                return await ctx.send("You aren't in the game!", ephemeral=True)
            if game.players.index(player) != 0:
                return await ctx.send("You must be the super player to quit the game!")
            await ctx.send("The game has been disbanded.")
            del game