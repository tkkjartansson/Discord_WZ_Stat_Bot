from discord.ext import commands
import discord
from DB_Interfaces.WZ_Stats_DB_Interface import DB_Interface
from API_Interfaces.WZ_Stats_API_Interface import API_Interface
from decimal import Decimal
from datetime import datetime
import os
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv('DISCORD_BOT_TOKEN')


bot = commands.Bot(command_prefix='!')

dbClient = DB_Interface()
apiClient = API_Interface()

@bot.event
async def on_ready():
    print("I'm ON THE LINE!")



@bot.command(name='getPlayerPlatforms', help='Returns a list of possible player platforms. These are case sensetive!')
async def getPlayerPlatforms(ctx):
    options = ['psn - [Playstation]','steam','xbl - [XBOX Live]','battle - [Battle.net]','acti - [Activision]']
    optionsString = '\n'.join(options)
    embed = discord.Embed(title="Player Platforms", description=optionsString, color=0x00ff00)

    await ctx.send(embed=embed)


@bot.command(name='Alias', help='Function that links your discord account with your Warzone account. You provide this function with your player name and platform. E.g if you use battle.net you can use: QWAAAAG#2496 battle. You can call the getPlayerPlatforms to get all available player platforms. Remeber the platform is case sensitive')
async def Alias(ctx, playerName, playerPlatform):

    userAlias = {
        'DiscordName'     : ctx.author.name,
        'DiscordId'       : ctx.author.id,
        'PlayerName'      : playerName,
        'PlayerPlatform'  : playerPlatform
    }
    dbClient.createUpdateAlias(userAlias)

    embed = discord.Embed(title="Success", color=0x00ff00)
    await ctx.send(embed=embed)

@bot.command(name='myStats', help='Fetches your lates stats and compares them to the last time you ran the function')
async def myStats(ctx):

    try:
        alias = dbClient.getAliasByDiscordId(ctx.author.id)
    except Exception as e:
        await ctx.send(str(e))
        return
        
    try:    
        stats = apiClient.getPlayerStats(alias['PlayerName'],alias['PlayerPlatform'])
    except Exception as e:
        await ctx.send(str(e))
        return

    hasPreviousStats= True

    try:
        previousStats = dbClient.getLatesStatLine(alias['id'])
    except Exception:
        hasPreviousStats = False



    embed = discord.Embed(title=f"{alias['PlayerName']} Stats",color=0x5E084D)
    if hasPreviousStats:

        statDiffs = {
            'Games'         : stats['gamesPlayed'] - previousStats['NumberOfGames'],
            'Kills'         : stats['kills'] - previousStats['Kills'],
            'Deaths'        : stats['deaths'] - previousStats['Deaths'],
            'KD_Ratio'      : round(Decimal(stats['kdRatio']) - Decimal(previousStats['KD_Ratio']), 3),
            'Score_Per_Min' : round(Decimal(stats['scorePerMinute']) - Decimal(previousStats['Score_Per_Min']),3),
            'Wins'          : stats['wins'] - previousStats['Wins'],
            'Avg_Kills'     : round(stats['kills']/stats['gamesPlayed']-previousStats['Kills']/previousStats['NumberOfGames'],2)
        }

        embed.add_field(name='Kills', value=f"{stats['kills']} ({statDiffs['Kills']} {getEmoji(statDiffs['Kills'])} )")
        embed.add_field(name='Avg Kills', value=f"{round(stats['kills']/stats['gamesPlayed'],2)} ( {statDiffs['Avg_Kills']} {getEmoji(statDiffs['Avg_Kills'])} )")
        embed.add_field(name='KDR', value=f"{round(stats['kdRatio'],2)} ( {statDiffs['KD_Ratio']} {getEmoji(statDiffs['KD_Ratio'])} )")  
        embed.add_field(name='Deaths', value=f"{stats['deaths']} ( {statDiffs['Deaths']} {getEmoji(statDiffs['Deaths'])} )", inline=False)

        embed.add_field(name='Number of games', value=f"{stats['gamesPlayed']} ( {statDiffs['Games']} {getEmoji(statDiffs['Games'])} )", inline=False)
        embed.add_field(name='Score per Minute',value=f"{round(stats['scorePerMinute'],2)} ({statDiffs['Score_Per_Min']} {getEmoji(statDiffs['Score_Per_Min'])} )", inline=False)
        embed.add_field(name='Wins',value=f"{stats['wins']} ({statDiffs['Wins']} {getEmoji(statDiffs['Wins'])} )", inline=False)

        embed.set_footer(text=f"Last update was {previousStats['CreatedOn'].strftime('%d.%m.%Y %H:%M')}")
    else:
        embed.add_field(name='Kills', value=stats['kills'])
        embed.add_field(name='Avg Kills', value=round(stats['kills']/stats['gamesPlayed'],2))
        embed.add_field(name='KDR', value=round(stats['kdRatio'],2))
        embed.add_field(name='Deaths', value=stats['deaths'], inline=False)
        
        

        embed.add_field(name='Number of games', value=stats['gamesPlayed'], inline=False)
        embed.add_field(name='Score per Minute',value=round(stats['scorePerMinute'],2), inline=False)
        embed.add_field(name='Wins',value=stats['wins'], inline=False)

    statLine = {
        'PlayerName'      : alias['PlayerName'],
        'NumberOfGames'   : stats['gamesPlayed'],
        'Wins'            : stats['wins'],
        'Kills'           : stats['kills'],
        'Deaths'          : stats['deaths'],
        'KD_Ratio'        : stats['kdRatio'],
        'Score_Per_Min'   : stats['scorePerMinute'],
        'CreatedOn'       : datetime.utcnow(),
        'WZ_Alias_Id'     : alias['id']
    }

    dbClient.createStatline(statLine)


    await ctx.send(embed=embed)

@bot.command(name='myWeeklyStats', help='Fetches your weekly stats')
async def myWeeklyStats(ctx):

    try:
        alias = dbClient.getAliasByDiscordId(ctx.author.id)
    except Exception as e:
        await ctx.send(str(e))
        return
        
    try:    
        stats = apiClient.getWeeklyStats(alias['PlayerName'],alias['PlayerPlatform'])
    except Exception as e:
        await ctx.send(str(e))
        return


    embed = discord.Embed(title=f"{alias['PlayerName']} Weekly stats",color=0x5E084D)
    embed.add_field(name='Kills', value=stats['kills'])
    embed.add_field(name='Avg Kills', value=round(stats['killsPerGame'],2))
    embed.add_field(name='KDR', value=round(stats['kdRatio'],2))
    embed.add_field(name='Deaths', value=stats['deaths'], inline=False)
    embed.add_field(name='Number of games', value=stats['matchesPlayed'], inline=False)
    embed.add_field(name='Score per Minute',value=round(stats['scorePerMinute'],2), inline=False)

    await ctx.send(embed=embed)



def getEmoji(value):
    if value>0:
        return '🟢'
    elif value < 0:
        return '🔴'
    else:
        return '⚪'


bot.run(TOKEN)