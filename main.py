import os
import requests
from flask import Flask, redirect, url_for, render_template, request, flash, jsonify
from threading import Thread

nftportal_key = os.environ['nftportal_key']
opensea_key = os.environ['opensea_key']
akapi_key = os.environ['akapi_key']
app = Flask(__name__, template_folder='html')


#send html page in response
@app.route('/')
def index():
    return render_template('index.html', api_key=akapi_key)
    # return "NFT Viewer App - Soon"


def run():
    app.run(host='0.0.0.0', port=8080)


# A route to return all of the available entries in our catalog.
@app.route('/v1/address', methods=['GET'])
def api_all():
    reply = []
    owner = '0x72d3a53f709652ee730ef9807fb4ab8771485a92'

    url = f"https://api.opensea.io/api/v1/assets?owner={owner}&order_direction=desc&offset=0&limit=20"

    response = requests.request("GET", url, headers={
        "X-API-KEY": opensea_key
    }).json()
    try:
        total_assets = len(response['assets'])
        reply.append({'total_assets': total_assets})

        for x in range(total_assets):
            print(response['assets'][x]['image_url'])
            data = {
                'name': response['assets'][x]['name'],
                'img': response['assets'][x]['image_url']
            }

            reply.append(data)

        if total_assets == 0:
            print('No owned NFTs')
            reply.append('No owned NFTs')

    except:
        print(response)
        reply.append(response)

    print(reply)
    return jsonify(reply)


@app.route('/v1/post', methods=['POST'])
def api_post():
    data = request.json

    assets = []
    owner = data["address"]

    url = f"https://api.opensea.io/api/v1/assets?owner={owner}&order_direction=desc&offset=0&limit=20"

    response = requests.request("GET", url, headers={
        "X-API-KEY": opensea_key
    }).json()

    try:
        total_assets = len(response['assets'])
        assets.append({'total_assets': total_assets})

        for x in range(total_assets):
            print(response['assets'][x]['image_url'])
            data = {
                'name': response['assets'][x]['name'],
                'img': response['assets'][x]['image_url']
            }

            assets.append(data)

        if total_assets == 0:
            print('No owned NFTs')
            assets.append('')

    except:
        print(response)
        assets.append(response)

    print(assets)
    return jsonify(assets)


@app.route('/NFTPortal', methods=['POST'])
def nftportal_api_post():
    data = request.json

    assets = []

    #if the data doesn't contain key named address then it's not a valid request
    if 'address' not in data:
        return 'Err: Invalid request. Provide Address.'
    else:
        owner = data["address"]

    if 'auth' not in data:
        return 'Err: Invalid request. Provide Authentication Key.'
    else:
        auth = data["auth"]

    if auth == akapi_key:
        url = f"https://api.nftport.xyz/v0/accounts/{owner}"

        response_eth = requests.request("GET",
                                        url,
                                        headers={
                                            'Content-Type': "application/json",
                                            'Authorization': nftportal_key
                                        },
                                        params={
                                            "chain": "ethereum"
                                        }).json()

        response_poly = requests.request("GET",
                                         url,
                                         headers={
                                             'Content-Type':
                                             "application/json",
                                             'Authorization': nftportal_key
                                         },
                                         params={
                                             "chain": "polygon"
                                         }).json()

        #loop for ethereum chain NFTs
        try:
            total_assets = len(response_eth['nfts'])
            assets.append({'total_assets': total_assets})

            for x in range(total_assets):
                print(response_eth['nfts'][x]['file_url'])
                data = {
                    'description': response_eth['nfts'][x]['description'],
                    'img': response_eth['nfts'][x]['file_url'],
                    'name': response_eth['nfts'][x]['name'],
                    'chain': 'Ethereum'
                }

                assets.append(data)

            if total_assets == 0:
                print('No owned NFTs on ETH Chain')
                assets.append('')

            #change link
            for x in range(1, len(assets)):
                if 'img' in assets[x]:
                    if assets[x]['img'][:4] == 'ipfs':
                        assets[x]['img'] = ipfs_link_changer(assets[x]['img'])
                        print(assets[x]['img'])
            else:
                print('Not a IPFS link')

        except:
            print(response_eth)
            assets.append(response_eth)

        #loop for polygon chain NFTs
        try:
            total_assets_poly = len(response_poly['nfts'])
            assets[0]['total_assets'] += total_assets_poly

            for x in range(total_assets_poly):
                print(response_poly['nfts'][x]['file_url'])
                data = {
                    'description': response_poly['nfts'][x]['description'],
                    'img': response_poly['nfts'][x]['file_url'],
                    'name': response_poly['nfts'][x]['name'],
                    'chain': 'Polygon'
                }

                assets.append(data)

            if total_assets_poly == 0:
                print('No owned NFTs on Polygon Chain')
                assets.append('')

        except:
            print(response_poly)
            assets.append(response_poly)

        for x in range(1, len(assets)):
            if 'img' in assets[x]:
                if assets[x]['img'][:4] == 'ipfs':
                    assets[x]['img'] = ipfs_link_changer(assets[x]['img'])
                    print(assets[x]['img'])
            else:
                print('Not a IPFS link')

        return jsonify(assets)
    else:
        return jsonify('Auth failed')


t = Thread(target=run)
t.start()


def ipfs_link_changer(url):
    #ipfs link changer from ipfs:// to https://ipfs.io/
    try:
        url = url.replace('ipfs://', 'https://ipfs.io/')
        return url
    except:
        print('Invalid IPFS links')
