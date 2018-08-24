import aiopg
import discord
import aiohttp
import json
import os
from discord.ext.commands import Bot

client = Bot(command_prefix='>>')
DEFAULT_IMAGE = "https://s3-us-west-2.amazonaws.com/superdeluxe.com/dankland/generators/-92598402-Maybeyesmaybeno.jpg"
store = {}


@client.event
async def on_ready():
    conn = await aiopg.connect(dsn=os.environ['DATABASE_URL'],loop=client.loop)
    db =  await conn.cursor()
    await db.execute("""
	CREATE TABLE IF NOT EXISTS recipes (
	title	TEXT,
	ingredients	TEXT,
	execution	TEXT,
	author	TEXT,
    image     TEXT
    );
    """)
    store['conn'] = conn
    store['db'] = db
    print('Logged in as '+client.user.name+' (ID:'+client.user.id+') | Connected to '+str(len(client.servers))+' servers | Connected to '+str(len(set(client.get_all_members())))+' users')

@client.group(pass_context=True)
async def skordo(ctx):
    if ctx.invoked_subcommand==None:
        await store['db'].execute("SELECT title,ingredients,execution,image,author FROM recipes ORDER BY RANDOM() LIMIT 1")
        res = await store['db'].fetchone()
        if res==None:
            return await client.say("Εεε μπομπο δεν εχω σκορδα τι να κανουμε")
        embed = discord.Embed(title=res[0])
        embed.add_field(name="Υλικά",value=res[1],inline=False)
        embed.add_field(name="Εκτέλεση",value=res[2],inline=False)
        embed.set_thumbnail(url=res[3])
        embed.set_footer(text="Με αγάπη απο τον "+res[4])
        return await client.say(embed=embed)

@skordo.command(pass_context=True)
async def add(ctx):
    await client.say("Πως το λενε το σκορδοψωμο ?")
    msg = await client.wait_for_message(timeout=60,author=ctx.message.author,channel=ctx.message.channel)
    title = msg.content[:24]
    await client.say("Τι χρειαζεται για να το φτιαξεις ?")
    msg = await client.wait_for_message(timeout=60,author=ctx.message.author,channel=ctx.message.channel)
    ingredients = msg.content[:1020:]+'...'
    await client.say("Πως φτιαχνεται ?")
    msg = await client.wait_for_message(timeout=60,author=ctx.message.author,channel=ctx.message.channel)
    execution = msg.content[:1020]+'...'
    await client.say("Χωσε και μια εικονα (ή πες οχι)")
    msg = await client.wait_for_message(timeout=60,author=ctx.message.author,channel=ctx.message.channel)
    if len(msg.attachments)>0:
        image = msg.attachments[0]['url']
    else:
        image = DEFAULT_IMAGE 
    await store['db'].execute("INSERT INTO recipes(title,ingredients,execution,image,author) values(?,?,?,?,?)",(title,ingredients,execution,image,str(ctx.message.author)))
    return await client.say("Εγινε μητσο")

@skordo.command()
async def help():
    return await client.say("""
    Λοιπον μαν απλα τα πραγματα
    >>skordo
    -Σου χωνει σκορδοψωμο
    >>skordo add
    -Προσθεσε το δικο σ σκορδοψωμο
    >>skordo credits
    -μπομπος
    >>skordo help
    -αυτο 
    """)

@skordo.command()
async def credits():
    return await client.say("""
    Με αγαπη και μαλακια απο τον tzatzikiweeb#7687
    https://gist.github.com/marios8543/b7d8ebaa4c3ca2abc6f8aa6f789cea81
    Requirements & Dependencies:
    - Python 3.5 or higher
    - discord.py (async branch)
    - aiosqlite3
""")

@skordo.command(pass_context=True)
async def search(ctx,*args):
    query = " ".join(args)
    await store['db'].execute("SELECT title,ingredients,execution,image,author FROM recipes WHERE title LIKE '%{q}%' OR ingredients LIKE '%{q}%'".format(**{'q':query}))
    res = await store['db'].fetchone()
    if res==None:
        return await client.say("Σορρυ μαν δεν εχω τπτ γ αυτο")
    embed = discord.Embed(title=res[0])
    embed.add_field(name="Υλικά",value=res[1],inline=False)
    embed.add_field(name="Εκτέλεση",value=res[2],inline=False)
    embed.set_thumbnail(url=res[3])
    embed.set_footer(text="Με αγάπη απο τον "+res[4])
    return await client.say(embed=embed)

if __name__=='__main__':
    client.run(os.environ['discord_token'])
