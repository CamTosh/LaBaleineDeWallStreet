import requests
import json
import getopt
import discord
import math
import os
from charts import Chart


client = discord.Client()
token = os.environ["DISCORD_TOKEN"]

rule = '\nQuelques règles du discord de la baleine :\n\
- Pas de pubs sans une autorisation des admins\n\
- Courtoisie et savoir-vivre sont de rigueur\n\
- Les calls **SANS ARGUMENT** seront suivis par un avertissement et ensuite un bannissement\n\
- Pensez aux gens qui vont vous lire et mettez-vous à leur place\n\
- Le flood et le troll sont interdits\n\
- Les commandes de prix, conv etc du bot sont uniquement autorisé dans le chan #bot\n\
- Les liens de parrainage sont interdits\n\n\n\
Commande du bot :\n\n\
\tBaleineDeWallStreet :\n\
\tprix -> price (market) coin\n\
\tconversion -> conv unité coin\n\
\tgraph -> chart coin\n\
\torder book -> book coin\n\n\
Lexique :\n\n\
\t!helpList \n\
\t!help Recherche\n'

chart = Chart()

class switch(object):
    """ Custom switch construction"""
    value = None
    def __new__(class_, value):
        class_.value = value
        return True

def case(*args):
    """ Custom switch case """
    return any((arg == switch.value for arg in args))


def calc(str):
    """ Calc command """
    str = str.replace('os.', '')
    str = str.split()
    str = str.remove('calc')
    return ''


def traitement(str):
    """ Using our custom switch on user entry """
    d = 0
    str = str.lower()
    if len(str.split()) > 1:
        while switch((str.split()[0]).lower()):
            if case('prix'):
                d = price(str.split())
                break
            if case('price'):
                d = price(str.split())
                break
            if case('conv'):
                d = conv(str.split())
                break
            if case('volume'):
                break
            if case('chart'):
                d = chart.chart(str.split()[1])
                break
            if case('book'):
                d = chart.book(str.split()[1])
                break
            break
    return d

def price(str):
    """ Break down price command """
    if len(str) >= 2:
        while switch(str[1]):
            if case('polo'):
                str.remove('polo')
                t = poloniex(str)
                break
            if case('trex'):
                str.remove('trex')
                t = bittrex(str)
                break
            if case('poloniex'):
                str.remove('poloniex')
                t = poloniex(str)
                break
            if case('bittrex'):
                str.remove('bittrex')
                t = bittrex(str)
                break
            if case('p'):
                str.remove('p')
                t = poloniex(str)
                break
            if case('b'):
                str.remove('b')
                t = bittrex(str)
                break
            t = lost(str)
            break
    return t

def conv(boo2):

    boo2.remove('conv')
    valBtc = btcrecup(0)
    valBtcE = btcrecup(1)
    try:  #si le nombre + la devise
        float(boo2[0])
        final=polorecup(boo2[1], 0)

        if(boo2[1].upper()=="BTC"):
            final=float(valBtc)*float(boo2[0])
            final2=float(valBtcE)*float(boo2[0])
            return ("```"+str(boo2[0])+" "+str(boo2[1]).upper()+" valent "+ str("%.2f" %final)+"$ ou "+str("%.2f" %final2)+"€```")

        if(final==0):
            final=bittrecup(boo2[1],0)
        if(final!=0):
            final2=(float(valBtcE)*(float(final)/float(valBtc)))*float(boo2[0])
            final=float(final)*float(boo2[0])
            final = "```"+str(boo2[0])+" "+str(boo2[1]).upper()+" valent "+ str("%.2f" %final)+"$ ou "+str("%.2f" %final2)+"€  ("+str("%.4f" %(final/valBtc))+"฿)```"

    except : #si la devise + le nombre
        try:
            float(boo2[1])
        except:
            boo2[1]=0

        if(boo2[0].upper()=="BTC"):
            final=float(valBtc)*float(boo2[1])
            final2=float(valBtcE)*float(boo2[1])
            print(1)
            return ("```"+str(boo2[1])+" "+str(boo2[0]).upper()+" valent "+ str("%.2f" %final)+"$ ou "+str("%.2f" %final2)+"€```")

        final=polorecup(boo2[0],0)
        if(final==0):
            final=bittrecup(boo2[0],0)

        if(final!=0):
            final2=(float(valBtcE)*(float(final)/float(valBtc)))*float(boo2[1])
            final=float(final)*float(boo2[1])
            final ="```"+str(boo2[1])+" "+str(boo2[0]).upper()+" valent "+  str("%.2f" %final)+"$ ou "+str("%.2f" %final2)+"€  ("+str("%.4f" %(final/valBtc))+"฿)```"

    return final



def bittrex(boo3):

    print("Trex Selector")

    i = 0
    final = ["","","","","",""]
    boo3.remove("price")

    nbreCase = len(boo3)

    offset = 0

    while nbreCase > i :

        final[offset]=bittrecup(boo3[i],1)

        if(final[offset]!=0):
            offset+=1

        i = 1 + i

    return final

def poloniex(boo3):

    print("Polo Selector")

    i = 0
    final = ["","","","","","","","","","","","","","","",""]

    boo3.remove("price")


    nbreCase = len(boo3)

    offset=0

    while nbreCase > i :

        final[offset]=polorecup(boo3[i],1)

        if(final[offset]!=0):
            offset+=1

        i = 1 + i
    return final

def finexrecup(boo4,all):

    url="https://api.bitfinex.com/v1/pubticker/"
    valBtc = btcrecup(0)
    market=boo4+"btc"
    print(market)
    content=requests.get(url+market)
    data=content.json()

    if("bid" in data):
        if(all):
            return("```"+boo4.upper()+"   "+str(data["last_price"])+"฿    $"+str("%.5f" %(float(data["last_price"])*float(valBtc)))+"  (Bitfinex)"+"```")
        else:
            return(data["last_price"]*valBtc)
    else:
        return 0


def lost(boo3):

    i = 0
    final = ["","","","","","","","","","","","","","","",""]
    boo3.remove("price")

    nbreCase = len(boo3)

    while nbreCase > i :

        final[i]=polorecup(boo3[i],1)

        if(final[i]==0):
            final[i]=bittrecup(boo3[i],1)
        if(final[i]==0):
            final[i]=finexrecup(boo3[i],1)

        i = 1 + i
    return final

def polorecup(boo4,all):

    market="BTC_"+boo4.upper()

    valBtc = btcrecup(0)
    valBtcE = btcrecup(1)

    if(market=="BTC_BTC"):
        value = "```1 BTC vaut "+str(valBtc)+"$"+" ou "+str(valBtcE)+"€```"
        return(value)

    url="https://poloniex.com/public?command=returnTicker"
    print("Poloniex Récup")

    content=requests.get(url)
    data=content.json()



    print(market)

    if(market in data):
        if(all):
            return("```"+boo4.upper()+"   "+data[market]["last"]+"฿ ("+str("%.2f" %(float(data[market]["percentChange"])*100))+"%) $"+(str("%.5f" %(float(data[market]["last"])*(float(valBtc)))))+" (Poloniex)"+"```")
        else:
            return(float(data[market]["last"])*valBtc)
    else:
        return 0


def bittrecup(boo4,all):

    print("Bittrex Recup")

    url="https://bittrex.com/api/v1.1/public/getmarketsummary?market="
    valBtc = btcrecup(0)
    market="btc-"+boo4
    print(market)
    content=requests.get(url+market)
    data=content.json()

    print(data["success"])

    if(data["success"]):

        if(all):
            print("all")
            percent1=((data["result"][0]["Last"])-(data["result"][0]["PrevDay"]))
            percent2=(percent1/float(data["result"][0]["PrevDay"]))*100



            return("```"+boo4.upper()+"   "+str(data["result"][0]["Last"])+"฿ ("+str("%.2f" %percent2)+"%) $"+str("%.5f" %(data["result"][0]["Last"]*float(valBtc)))+"  (Bittrex)"+"```")
        else:
            return(data["result"][0]["Last"]*valBtc)
    else:
        return 0

def btcrecup(euro):
    """ Get BTC price"""
    if(euro):
        url = 'https://www.bitstamp.net/api/v2/ticker/btceur/'
    else:
        url = 'https://www.bitstamp.net/api/v2/ticker/btcusd/'
    content = requests.get(url)
    data = content.json()
    if ("last" in data):
        return (float(data["last"]))
    else:
        return 0



@client.event
async def on_message(message):
    if message.content.startswith(('price', 'Price', 'prix', 'Prix', 'conv', 'Conv', 'chart', 'Chart', 'book', 'Book')):
        if str(message.channel) != 'bot':
            roles = [i.name for i in message.author.roles]
            if 'Baleine novice' in roles:
                await client.send_message(
                    message.author,
                    'Es-tu sûr de respecter les règles d\'utilisation du bot ? ;)'
                )

    if message.content.startswith(('price','Price','prix','Prix')):
        await client.send_typing(message.channel)
        retour=traitement(message.content)
        for ret in retour:
            if ret:
                await client.send_message(
                    message.channel,
                    retour[i]
                )

    if message.content.startswith(('conv','Conv')):
        await client.send_typing(message.channel)
        retour=traitement(message.content)
        if retour:
            await client.send_message(
                message.channel,
                retour
            )

    if message.content.startswith(('calc','Calc')):
        retour=calc(message.content)
        await client.send_message(
            message.channel,
            "```"+ ((message.content).split())[1]+ " = " + str("%.2f" %retour)+"```"
        )

    if message.content.startswith(('chart','Chart')):
        await client.send_typing(message.channel)
        retour = traitement(message.content)
        if retour:
            await client.send_file(
                message.channel,
                retour
            )
            os.remove(retour)

    if message.content.startswith(('book', 'Book')):
        await client.send_typing(message.channel)
        retour = traitement(message.content)
        if retour:
            await client.send_file(
                message.channel,
                retour
            )
            os.remove(retour)

    if message.content.startswith(('/rules', '!rules', 'rule', '!règles', 'rules', 'Rules')):
        await client.send_message(message.author, rule)

@client.event
async def on_ready():

    print('Logged in as :')
    print(client.user.name)
    print(client.user.id)

client.run(token)
