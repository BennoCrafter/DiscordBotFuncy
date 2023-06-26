import discord
from discord.ext import commands
from DiscordLevelingCard import RankCard, Settings
import json


class Bot:
    def __init__(self):
        self.config_filename = "config.json"
        self.load_config()
        self.rankings = self.load_rankings()
        self.sorted_ranks = sorted(self.rankings.values())[::-1]
        self.sorted_useres = sorted(self.rankings, key=self.rankings.get)[::-1]
        self.card_settings = Settings(background="background.jpeg",
                                      text_color="white",
                                      bar_color="white")
        self.bot = commands.Bot(command_prefix='.',
                                intents=discord.Intents().all())

    def load_config(self):
        with open(self.config_filename) as f:
            data = json.load(f)
            self.channel_id_to_react = data["channel_id_to_react"]
            self.reactions = data["reactions"]
            self.rankings_file = data["rankings_file"]
            self.exp_to_level_up = data["exp_to_level_up"]
        f.close()

        with open("privat_config.json") as f:
            data = json.load(f)
            self.token = data["token"]
        f.close()

    def load_rankings(self):
        try:
            with open(self.rankings_file, 'r') as file:
                return json.load(file)
        except FileNotFoundError:
            return {}

    def save_rankings(self, rankings):
        with open(self.rankings_file, 'w') as file:
            json.dump(rankings, file)
        file.close()
        self.sorted_ranks = sorted(self.rankings.values())
        self.sorted_useres = sorted(self.rankings, key=self.rankings.get)


if __name__ == "__main__":
    bot = commands.Bot(command_prefix='.', intents=discord.Intents().all())
    bot_info = Bot()


    @bot.command()
    async def rank(ctx, user_to_rank=None):
        print(user_to_rank)
        user_id = str(ctx.author.id)
        if user_to_rank is None:
            user = ctx.author
        else:
            user_id = str(user_to_rank).replace("<",
                                                "").replace(">",
                                                            "").replace("@", "")
            user = await bot.fetch_user(int(user_id))
            print(user)
        if user_id in bot_info.rankings:
            user_ranking = bot_info.rankings[user_id]
            await ctx.defer()
            print(user)
            a = RankCard(settings=bot_info.card_settings,
                         avatar=user.display_avatar.url,
                         level=user_ranking[0],
                         current_exp=user_ranking[1],
                         max_exp=bot_info.exp_to_level_up,
                         username=user.name,
                         rank=int(bot_info.sorted_useres.index(user_id)) + 1)
            image = await a.card3()
            await ctx.send(file=discord.File(image, "level_card.png"))
        else:
            await ctx.send('You do not have a ranking yet.')


    @bot.command()
    async def leaderboard(ctx):
        if len(bot_info.sorted_useres) < 10:
            x = len(bot_info.sorted_useres)
        else:
            x = 10
        embedVar = discord.Embed(title="Rankings",
                                 description="A leaderboard",
                                 color=0x00ff00)
        for i in range(x):
            user = await bot.fetch_user(int(bot_info.sorted_useres[i]))
            embedVar.add_field(name=f"#{i + 1}", value=user, inline=False)
        await ctx.send(embed=embedVar)


    @bot.event
    async def on_ready():
        print(f'Logged in as {bot.user.name}')


    @bot.event
    async def on_member_join(member):
        channel = member.guild.get_channel(1026403341753909278)
        fmt = f"Hey {member.mention}, schön dass du Kunst Café🌷 gejoint bist! 🥳\n\nDu kannst gerne https://discord.com/channels/1026383599139835924/1026403423437987910 geben.\n\nBitte halte dich an die https://discord.com/channels/1026383599139835924/1026403289627111424\n\nViel Spaß dir 😊"
        await channel.send(fmt.format(member=member))


    @bot.event
    async def on_message(message):
        if message.author.bot:
            return

        await bot.process_commands(message)

        user_id = str(message.author.id)
        if user_id not in bot_info.rankings:
            bot_info.rankings[user_id] = [0, 0]
        bot_info.rankings[user_id][1] += len(message.content)
        if bot_info.rankings[user_id][1] >= bot_info.exp_to_level_up:
            bot_info.rankings[user_id][0] += 1
            bot_info.rankings[user_id][1] -= bot_info.exp_to_level_up
        bot_info.save_rankings(bot_info.rankings)

        # react to pictures
        if message.channel.id == bot_info.channel_id_to_react:
            if message.attachments:
                for reaction in bot_info.reactions:
                    await message.add_reaction(reaction)

        # counting
        if message.channel.id == channel_id_to_count:
            if int(message.content) == (bot_info.current_count + 1):
                bot_info.current_count += 1
                await message.add_reaction("✅")

bot.run(bot_info.token)
