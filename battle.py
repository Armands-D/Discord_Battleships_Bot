import discord
from time import sleep

playing = {}
discord_emojis = {
    #" " : "💧",
    0 : ":zero:",
    1 : ":one:",
    2 : ":two:",
    3 : ":three:",
    4 : ":four:",
    5 : ":five:",
    6 : ":six:",
    7 : ":seven:",
    #  "|" : "❕",
    #  "─" : "➖",
    # "sF" : ":ferry:",
    # "sf" : ":ship:",
    # "sT" : ":sailboat:",
    # "st" : ":canoe:",
    # "bb" : "💥",
    # "xx" : "❌"
}

red = 0xff1900
yellow = 0xfff700
green = 0x44ff00
cyan = 0x00fffb

ships_to_place = [
    ":asterisk: :one: : " + (":ferry:" * 5),
    ":asterisk: :one: : " + (":ship:" * 4),
    ":asterisk: :two: : " + (":sailboat:" * 3),
    ":asterisk: :two: : " + (":canoe:" * 2)
]


class Board(object):
    top = ["0", "1", "2", "3", "4", "5", "6", "7"]

    def __init__(self):
        self.a = ["💧", "💧", "💧", "💧", "💧", "💧", "💧", "💧"]
        self.b = ["💧", "💧", "💧", "💧", "💧", "💧", "💧", "💧"]
        self.c = ["💧", "💧", "💧", "💧", "💧", "💧", "💧", "💧"]
        self.d = ["💧", "💧", "💧", "💧", "💧", "💧", "💧", "💧"]
        self.c = ["💧", "💧", "💧", "💧", "💧", "💧", "💧", "💧"]
        self.d = ["💧", "💧", "💧", "💧", "💧", "💧", "💧", "💧"]
        self.e = ["💧", "💧", "💧", "💧", "💧", "💧", "💧", "💧"]
        self.f = ["💧", "💧", "💧", "💧", "💧", "💧", "💧", "💧"]
        self.g = ["💧", "💧", "💧", "💧", "💧", "💧", "💧", "💧"]
        self.h = ["💧", "💧", "💧", "💧", "💧", "💧", "💧", "💧"]
        self.full = [self.a, self.b, self.c, self.d, self.e, self.f, self.g, self.h]

    def return_board(self):
        s = "➖❕" + "❕".join(Board.top)
        #sep = "\n➖" + "➖" * 8 + "❕\n"
        sep = "\n" + ("__" * 4) + "\n"
        s += sep
        i = 0
        for item in self.full:
            s += Board.top[i]
            tmp = ""
            for cr in item:
                tmp += cr + "❕"
            s += "❕" + tmp[:-1] + sep
            i += 1
        return s[:-1]

    def discordify(self):
        s = self.return_board()
        print(s)
        for k, v in discord_emojis.items():
            s = s.replace(str(k), v)
        return s

    def place(self, x1, y1, x2, y2, ship):
        if x1 != x2:
            if x1 > x2:
                mx = x1
                lx = x2
            else:
                mx = x2
                lx = x1
            
            row = self.full[y1]
            for i in range(lx, mx + 1):
                if not isinstance(row[i], str):
                    return False
            for i in range(lx, mx + 1):
                row[i] =  ship
            self.full[y1] = row
            ship.ready = True
            return True

        else:
            if y1 > y2:
                my = y1
                ly = y2
            else:
                my = y2
                ly = y1

            for i in range(ly, my + 1):
                if not isinstance(self.full[i][x1], str):
                    return False
            for i in range(ly, my + 1):
                self.full[i][x1] =  ship
            ship.ready = True
            return True

    @staticmethod
    async def attack(player, x, y):
        playing[player.id]["played"].add(str(x) + str(y))
        opponent = playing[player.id]["opp"]
        opp_ship_layout = playing[opponent.id]["board"].full
        if not isinstance(opp_ship_layout[y][x], str):
            playing[opponent.id]["board"].full[y][x].hits += 1
            if playing[opponent.id]["board"].full[y][x].hits == playing[opponent.id]["board"].full[y][x].length:
                playing[opponent.id]["board"].full[y][x].dead = True
            playing[player.id]["guess"].full[y][x] = "💥"
            playing[opponent.id]["board"].full[y][x] = "💥"
            embed = discord.Embed(title="THAT'S A HIT", description="", color=green)
            await player.dm_channel.send(embed=embed)
            embed = discord.Embed(title="THEY'VE HIT YOUR SHIP", description="", color=red)
            await opponent.dm_channel.send(embed=embed)
            miss = False

        else:
            playing[player.id]["guess"].full[y][x] = "❌"
            playing[opponent.id]["board"].full[y][x] = "❌"
            embed = discord.Embed(title="THAT'S A MISS", description="", color=red)
            await player.dm_channel.send(embed=embed)
            embed = discord.Embed(title="THEY'VE MISSED YOUR SHIP", description="", color=green)
            await opponent.dm_channel.send(embed=embed)
            miss = True

        playing[opponent.id]["turn"] = True
        playing[player.id]["turn"] = False
        return miss


async def send_player_board(player, board_name):
        b = playing[player.id][board_name].discordify()
        if board_name != "board":
            t = "YOUR GUESSING BOARD"
            c = cyan
        else:
            t = "YOUR PLACEMENT BOARD"
            c = yellow
        embed = discord.Embed(title=t, description=b, color=c)
        embed.set_footer(text="Use !h for help : You're Playing against " + playing[player.id]["opp"].name)
        await player.dm_channel.send(embed=embed)

async def ships_hit(opponent, player):
    ship_list = playing[player.id]["ships"]
    tmp = 0
    s = ""
    for ship in ship_list:
        if ship.length == tmp:
            s += "-----" + (":boom:" * ship.hits) + (ship.__str__() * (ship.length - ship.hits ))
        else:
            s += "\n" + (":boom:" * ship.hits) + (ship.__str__() * (ship.length - ship.hits ))
        tmp = ship.length
    embed = discord.Embed(title="ENEMY SHIPS YOU'VE HIT", description=s, color=red)
    await opponent.dm_channel.send(embed=embed)
    #await opponent.dm_channel.send(s)

async def setup(p1, p2):
    text = ships_to_place[0] + "  :arrow_left:\n" + "\n".join(ships_to_place[1:])
    embed = discord.Embed(title="SHIPS TO PLACE", description=text, color=yellow)

    if p1.dm_channel is None:
        await p1.create_dm()
        await send_player_board(p1, "board")
        await p1.dm_channel.send(embed=embed)
    else:
        await send_player_board(p1, "board")
        await p1.dm_channel.send(embed=embed)

    if p2.dm_channel is None:
        await p2.create_dm()
        await send_player_board(p2, "board")
        await p2.dm_channel.send(embed=embed)
    else:
        pass
        await send_player_board(p2, "board")
        await p2.dm_channel.send(embed=embed)

async def ship_count(player, ship, ships_to_place):
    i = abs(ship.length - 5)
    s = ""
    for x in range(len(ships_to_place)):
        if x < i:
            s += "\n" + ships_to_place[x] + "  :white_check_mark:"
        elif x == i:
            s += "\n" + ships_to_place[x] + "  :arrow_left:"
        else:
            s += "\n" + ships_to_place[x]
    embed = discord.Embed(title="SHIPS TO PLACE", description=s, color=yellow)
    await player.dm_channel.send(embed=embed)


class Ship5(object):
    def __init__(self):
        self.length = 5
        self.hits = 0
        self.ready = False
        self.dead = False

    def __str__(self):
        return "⛴️"

    def __add__(self, a):
        return self.__str__() + a

class Ship4(object):
    def __init__(self):
        self.length = 4
        self.hits = 0
        self.ready = False
        self.dead = False

    def __str__(self):
        return "🚢"

    def __add__(self, a):
        return self.__str__() + a

class Ship3(object):
    def __init__(self):
        self.length = 3
        self.hits = 0
        self.ready = False
        self.dead = False

    def __str__(self):
        return "⛵"

    def __add__(self, a):
        return self.__str__() + a

class Ship2(object):
    def __init__(self):
        self.length = 2
        self.hits = 0
        self.ready = False
        self.dead = False

    def __str__(self):
        return "🛶"

    def __add__(self, a):
        return self.__str__() + a
