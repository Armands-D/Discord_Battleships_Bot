import discord
from dotenv import load_dotenv
import os

from battle import *
from re import findall

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN_GAMEBOT')
GUILD = os.getenv('DISCORD_GUILD_GAMEBOT')

# Armands
admins = {315480446345674753}

client = discord.Client()

@client.event
async def on_ready():
    for guild in client.guilds:
        if guild.name == GUILD:
            break

    print(
        f'{client.user} is connected to the following guild:\n'
        f'{guild.name}(id: {guild.id})'
    )
    await client.change_presence(activity=discord.Activity(type=discord.ActivityType.listening, name=" !h for help"))

prefix = "!"
@client.event
async def on_message(message):

    if (prefix + "h") in message.content:
        # Simple Help command explaining the commands used to play
        tit = "HOW TO USE BATTLE BOT TO PLAY BATTLESHIPS"
        commands_dic = {
            "**!w @player_mention**"  : "This command starts a battle with the mentioned player, if they're not already playing with somebody or if they're not a bot. This is a server specific command",
            "**!p x1 y1 x2 y2**"  : "This command places your current ship, x1, y1 is the coordinate of the ship you're trying to place will start at and x2, y2 is where the ship will stop. x1, y1, x2, y2 can be written in any format, with or without spaces, commas brackets etc.. aslong as the distance between the points is the length of the ship you're trying to place.",
            "**!a x1 y1**"  : "This command is used to attack and guess where your opponent placed their ships, this command only works when both players placed all their ships and players will take turns. This command can also be written with or without, spaces, commas brackets, etc...",
            "**!quit**" : "This command quits you from your current game, meaning you no longer are playing and neither is your opponent. ",
        }
        embed = discord.Embed(title=tit, description="", color=green)
        for command in commands_dic:
            embed.add_field(name=command, value=commands_dic[command], inline=False)
        embed.set_footer(text="\nYou can use all commands in the server chat or DM battle bot. Except for !w which needs to be in the server chat.")
        await message.channel.send(embed=embed)

    if (prefix + "w").casefold() in message.content:
        # !w @1mention
        if len(message.raw_mentions) == 1:
            # Checks for only 1 mention
            p1 = message.author
            p2 = message.mentions[0]
            # Pervents Battling self
            if p1.id != p2.id: # add in and not p2.bot and not p1.bot
                if p1.id not in playing and p2.id not in playing:
                    # Add player id's as key to a dic and several variables unique to each player as values
                    # Board is the board players will use to place their boats
                    # Opp is the opponent's discord user class, to keep track who you're battling
                    # Ready is False unless all boats have been placed
                    # Ships is a list of all the ships(classes) the players will have to palce
                    # Guess is a blank board players will use to guess where the oponent placed their ships
                    # Turn is is set True for the player who's turn it is to guess and false otherwise
                    # Played is a set of coordinates that that players has already guessed, pervents duplicate guesses
                    playing[p1.id] = {"board" : Board(), "opp" : p2, "ready" : False, "ships" : [Ship5(), Ship4(), Ship3(), Ship3(), Ship2(), Ship2()], "guess" : Board(), "turn" : True, "played" : set()}
                    playing[p2.id] = {"board" : Board(), "opp" : p1, "ready" : False, "ships" : [Ship5(), Ship4(), Ship3(), Ship3(), Ship2(), Ship2()], "guess" : Board(), "turn" : False, "played" : set()}
                    await setup(p1, p2)

    # !p (x1, y1) (x2, y2)
    if (prefix + "p").casefold() in message.content and message.author.id in playing and not playing[message.author.id]["ready"]:
        # Checks if author of message is playing and that they haven't already placed all their ships
        msgid = message.author.id
        coor = findall(r"[0-7]", message.content)
        # list of [x1, y1, x2, y2] coordinates given
        if len(coor) == 4:
            coor = [int(c) for c in coor]
            x1, y1 = coor[0], coor[1]
            x2, y2 = coor[2], coor[3]

            ship_rdy_states = [ship.ready for ship in playing[msgid]["ships"]]
            ship = playing[msgid]["ships"][ship_rdy_states.index(False)]
            # First that hasn't been placed in players list of ships
            if ((x1 == x2) and (abs(y2 - y1) == ship.length - 1))^ ((y1 == y2) and (abs(x1 - x2) == ship.length - 1)):
                # Checks if either the x or y values changes but not both, to avoid diagonal placement
                # Checks if the distance between given coordinates is the same size as the ship they're trying to place
                if Board.place(playing[msgid]["board"], x1, y1, x2, y2, ship):
                    await send_player_board(message.author, "board")
                    # Sends player Their board if the placement is valid  
                    ship_rdy_states = [ship.ready for ship in playing[msgid]["ships"]]
                    if False in ship_rdy_states:
                        # Checks if all ships have been placed, if not messages player ships to place
                        ship = playing[msgid]["ships"][ship_rdy_states.index(False)]
                        await ship_count(message.author, ship, ships_to_place)
                    
                    else:
                        playing[msgid]["ready"] = True
                        embed = discord.Embed(title="ALL SHIPS PLACED", description="", color=green)
                        await message.author.dm_channel.send(embed=embed)
                        await send_player_board(message.author, "guess")
                        # Sends player their guessing board, denotating they're ready and all ships have been placed
                        text = "Player : " + message.author.name + " is ready "
                        embed = discord.Embed(title=text, description="", color=green)
                        await playing[message.author.id]["opp"].dm_channel.send(embed=embed)
                        # Sends Opponent a message that the other player is ready
                    

    if (prefix + "a").casefold() in message.content and message.author.id in playing and playing[message.author.id]["ready"] and playing[playing[message.author.id]["opp"].id]["ready"] and playing[message.author.id]["turn"]:
        coor = findall(r"[0-7]", message.content)
        if len(coor) == 2:
            if coor[0] + coor[1] not in playing[message.author.id]["played"]:
                [x, y] = [int(coor[0]), int(coor[1])]
                player = message.author
                opponent = playing[player.id]["opp"]
                if not await Board.attack(player, x, y): # if not miss
                    await ships_hit(player, opponent)
                check = [ship.dead for ship in playing[opponent.id]["ships"]]
                if all(check):
                    s = ":balloon: :tada: !!! YOU WIN !!! :tada: :balloon:"
                    embed = discord.Embed(title=":first_place: WINNER :first_place:", description=s, color=green)
                    await player.dm_channel.send(embed=embed)

                    s = ":joy: !!! YOU LOST BADLY !!! :joy:"
                    embed = discord.Embed(title=":flag_white: LOSS LEADER :flag_white:", description=s, color=red)
                    await opponent.dm_channel.send(embed=embed)
                    playing.pop(message.author.id)
                    playing.pop(opponent.id)
                else:
                    await send_player_board(opponent, "board")
                    await send_player_board(opponent, "guess")
                    await ships_hit(opponent, player)
                    embed = discord.Embed(title="YOUR TURN TO ATTACK", description="", color=green)
                    await opponent.dm_channel.send(embed=embed)  


    if prefix + "quit" in message.content:
        if message.author.id in playing:
            opponent = playing[message.author.id]["opp"]
            opp_id = opponent.id
            playing.pop(opp_id)
            playing.pop(message.author.id)
            embed = discord.Embed(title="YOU QUIT YOUR MATCH", description="", color=red)
            await message.author.dm_channel.send(embed=embed)  
            embed = discord.Embed(title="YOUR OPPONENT QUIT THE MATCH", description="", color=red)
            await opponent.dm_channel.send(embed=embed)
            # Removes player and opponent from playing dic and messages both players

client.run(TOKEN)

# Sends Guess Board Twice >/
# Say when it's the person's turn >/
# Show when a players ship has been hit >/
# if hits player goes again
# Say if opponent missed >/
# depending on how many ships you hit have different win and loss messages
# Letters intead of numbers
# Copy and past actual empojis instead of using :emojinname:
# Message when other player is ready
# Error msg for wrong coordinates
# Make player inform emjois smaller ad leading spaces
# Embed board
# random hit messages
# axlamation changed to coloured square for grid, small squares
# show where you played your ships when guessing
# add fields to imbed to notify misses
# have to tell what ship type you hit
# send in channel if player put a ship down
