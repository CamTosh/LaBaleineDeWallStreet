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


def calc(str_usr):
    """ Calc command """
    str_usr = str_usr.replace('os.', '')
    str_usr = str_usr.split()
    str_usr = str_usr.remove('calc')
    return ''


def traitement(str_usr):
    """ Using our custom switch on user entry """
    d = 0
    str_usr = str_usr.lower()
    if len(str_usr.split()) > 1:
        while switch((str_usr.split()[0]).lower()):
            if case('prix'):
                d = price(str_usr.split())
                break
            if case('price'):
                d = price(str_usr.split())
                break
            if case('conv'):
                d = conv(str_usr.split())
                break
            if case('volume'):
                break
            if case('chart'):
                d = chart.chart(str_usr.split()[1])
                break
            if case('book'):
                d = chart.book(str_usr.split()[1])
                break
            break
    return d

def price(str_usr):
    """ Break down price command """
    if len(str_usr) >= 2:
        while switch(str_usr[1]):
            if case('polo'):
                str_usr.remove('polo')
                t = poloniex(str_usr)
                break
            if case('trex'):
                str_usr.remove('trex')
                t = bittrex(str_usr)
                break
            if case('poloniex'):
                str_usr.remove('poloniex')
                t = poloniex(str_usr)
                break
            if case('bittrex'):
                str_usr.remove('bittrex')
                t = bittrex(str_usr)
                break
            if case('p'):
                str_usr.remove('p')
                t = poloniex(str_usr)
                break
            if case('b'):
                str_usr.remove('b')
                t = bittrex(str_usr)
                break
            t = lost(str_usr)
            break
    return t

def conv(str_usr):

    str_usr.remove("conv")
    val_btc, val_btc_e = btcrecup()

    try:  #si le nombre + la devise
        float(str_usr[0])
        if str_usr[1].upper() == 'BTC':
            amount_dollars = val_btc * float(str_usr[0])
            amount_euros = val_btc_e * float(str_usr[0])
            verb = 'vaut' if str_usr[0] == '1' else 'valent'
            ret = '```{} {} {} {:.2f}$ ou {:.2f}€```'.format(
                str_usr[0],
                str_usr[1].upper(),
                verb,
                amount_dollars,
                amount_euros
            )
            return ret
        final = polorecup(str_usr[1], 0)
        if not final:
            final = bittrecup(str_usr[1], 0)
        if not final:
            final = finexrecup(str_usr[1], 0)

        if final:
            amount_dollars = float(final) * float(str_usr[0])
            amount_euros = float(final) * float(str_usr[0]) * val_btc_e / val_btc
            verb = 'vaut' if str_usr[0] == '1' else 'valent'
            ret = '```{} {} {} {:.2f}$ ou {:.2f}€ ({:.4f}฿)```'.format(
                str_usr[0],
                str_usr[1].upper(),
                verb,
                amount_dollars,
                amount_euros,
                amount_dollars / val_btc
            )
        else:
            ret = 'Je n\'ai pas trouvé la monnaie {}.'.format(str_usr[1].upper())
    except: #si la devise + le nombre
        try:
            float(str_usr[1])
        except:
            str_usr[1] = 0

        if str_usr[0].upper() == 'BTC':
            amount_dollars = val_btc * float(str_usr[1])
            amount_euros = val_btc_e * float(str_usr[1])
            verb = 'vaut' if str_usr[1] == 1 else 'valent'
            ret = '```{} {} {} {:.2f}$ ou {:.2f}€```'.format(
                str_usr[1],
                str_usr[0].upper(),
                verb,
                amount_dollars,
                amount_euros
            )
            return ret

        final = polorecup(str_usr[0], 0)
        if not final:
            final = bittrecup(str_usr[0], 0)
        if not final:
            final = finexrecup(str_usr[0], 0)

        if final:
            amount_dollars = float(final) * float(str_usr[1])
            amount_euros = float(final) * float(str_usr[1]) * val_btc_e / val_btc
            verb = 'vaut' if str_usr[1] == 1 else 'valent'
            ret = '```{} {} {} {:.2f}$ ou {:.2f}€ ({:.4f}฿)```'.format(
                str_usr[1],
                str_usr[0].upper(),
                verb, amount_dollars,
                amount_euros,
                amount_dollars / val_btc
            )
        else:
            ret = 'Je n\'ai pas trouvé la monnaie {}.'.format(str_usr[0].upper())
    return ret

def bittrex(str_usr):
    str_usr.remove('price')
    final = [bittrecup(cur, 1) for cur in str_usr]
    final = [fin for fin in final if fin]
    return final

def poloniex(str_usr):
    str_usr.remove('price')
    final = [polorecup(cur, 1) for cur in str_usr]
    final = [fin for fin in final if fin]
    return final

def finexrecup(str_usr, verbose):
    market = '{}btc'.format(str_usr)
    url = 'https://api.bitfinex.com/v1/pubticker/{}'.format(market)
    val_btc, _ = btcrecup()
    content = requests.get(url)
    data = content.json()
    if ("bid" in data):
        if verbose:
            ret = '```{} {}฿ ${:.5f} (Bitfinex)```'.format(
                str_usr.upper(),
                data['last_price'],
                val_btc * data['last_price']
            )
        else:
            ret = data['last_price'] * val_btc
    else:
        ret = 0
    return ret


def lost(str_usr):
    str_usr.remove('price')
    ret = []
    for cur in str_usr:
        fin = polorecup(cur, 1)
        if not fin:
            bittrecup(cur, 1)
        if not fin:
            finexrecup(cur, 1)
        if fin:
            ret.append(fin)
    return ret

def polorecup(str_usr, verbose):
    market = 'BTC_{}'.format(str_usr.upper())
    val_btc, val_btc_e = btcrecup()
    if market == 'BTC_BTC':
        ret = '```1 BTC vaut {}$ ou {}€```'.format(val_btc, val_btc_e)
        return ret
    url = 'https://poloniex.com/public?command=returnTicker'
    content = requests.get(url)
    data = content.json()
    if data[market]:
        if verbose:
            ret = '```{} {}฿ ({:.2f}%) ${:.5f} (Poloniex)```'.format(
                str_usr.upper(),
                data[market]['last'],
                data[market]['percentChange'] * 100,
                data[market]['last'] * val_btc
            )
        else:
            ret = val_btc * data[market]['last']
    else:
        ret = 0
    return ret


def bittrecup(str_usr, verbose):
    market = 'btc-{}'.format(str_usr)
    url = 'https://bittrex.com/api/v1.1/public/getmarketsummary?market={}'.format(market)
    val_btc, _ = btcrecup()
    content = requests.get(url)
    data = content.json()
    if data['success']:
        if verbose:
            perc = 100 * (data['result'][0]['Last']) - (data['result'][0]['PrevDay']) / data['result'][0]['PrevDay']
            ret = '```{} {}฿ ({:.2f}%) ${:.5f} (Bittrex)```'.format(
                str_usr.upper(),
                data['result'][0]['Last'],
                perc,
                data['result'][0]['Last'] * val_btc
            )
        else:
            ret = data['result'][0]['Last'] * val_btc
    else:
        ret = 0
    return ret

def btcrecup():
    """ Get BTC price"""
    url = 'https://min-api.cryptocompare.com/data/price?fsym=BTC&tsyms=BTC,USD,EUR'
    content = requests.get(url)
    data = content.json()
    return data['EUR'], data['USD']

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

    if message.content.startswith(('price', 'Price', 'prix', 'Prix')):
        await client.send_typing(message.channel)
        retour = traitement(message.content)
        for ret in retour:
            if ret:
                await client.send_message(
                    message.channel,
                    ret
                )

    if message.content.startswith(('conv', 'Conv')):
        await client.send_typing(message.channel)
        retour = traitement(message.content)
        if retour:
            await client.send_message(
                message.channel,
                retour
            )

    if message.content.startswith(('calc', 'Calc')):
        retour = calc(message.content)
        await client.send_message(
            message.channel,
            '```{} = {}```'.format(
                message.content.split()[1],
                retour
            )
        )

    if message.content.startswith(('chart', 'Chart')):
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
