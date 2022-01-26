import discord
from discord.ext import commands
import pymongo
import config

intents = discord.Intents.default()
intents.members = True

bot = commands.Bot(command_prefix='?', intents=intents)

client = pymongo.MongoClient(config.mongoKey)
db = client['discordTest']
 
@bot.event
async def on_ready():
    print('Logged in as')
    print(bot.user.name)
    print(bot.user.id)
    print('------')
   

@bot.command()
async def follow(ctx, *users):

    collection = db[ctx.author.id]

    for user in users:

        #update users collection
        qurey = {'name': user}
        if collection.find(qurey).limit(1).size()<=0:
            userDetails = {
                'name': user,
                'following': True
            }
            collection.insert_one(userDetails)
        else:
            collection.update_one({'name':user}, {"$set":{'following':True}}, upsert=True)

        #update followers collections
        if db[user].find({'name': ctx.author.id}).limit(1).size()<=0:
            userDetails = {
                'name': user,
                'follower': True
            }
            collection.insert_one(userDetails)
        else:
            collection.update_one({'name':ctx.author.id}, {"$set":{'follower':True}}, upsert=True)

    await ctx.send('You have followed {} users:'.format(len(users), ', '.join(users)))


@bot.command()
async def unfollow(ctx, *users):

    collection = db[ctx.author.id]

    #update users collection
    for user in users:
        qurey = {'name': user}
        if collection.find(qurey).limit(1).size()<=0:
            await ctx.send('Error: You are not following this user')
        else:
            collection.update_one({'name':ctx.author.id}, {"$set":{'following':False}}, upsert=False)
           

    #update followers collections
        if db[user].find({'name': ctx.author.id}).limit(1).size()<=0:
            userDetails = {
                'name': ctx.author.id,
                'follower': False
            }
            collection.insert_one(userDetails)
        else:
            collection.update_one({'name':ctx.author.id}, {"$set":{'follower':False}}, upsert=False)
    
@client.event
async def on_voice_state_update(member, before, after):
    if not before.channel and after.channel:
        collection = db[member]
        qurey = {'follower': True}
        notifyList = []
        for user in collection.find(qurey):
            notifyList.append(user['name'])

        #TODO, do wahtever u want with this list

bot.run('token')