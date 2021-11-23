import urllib.request, json, time, random,gzip, os
from twilio.rest import Client

def trigger_pubsub(event, context):

    found = False

    account_sid = os.environ['TWILIO_ACCOUNT_SID']
    auth_token = os.environ['TWILIO_AUTH_TOKEN']
    client = Client(account_sid, auth_token)

    twilio_from_number = os.environ['TWILIO_FROM_NUMBER']
    twilio_to_number = os.environ['TWILIO_TO_NUMBER']

    class sku: 
        def __init__(self, name, url, skuId, modelId): 
            self.name = name 
            self.url = url
            self.skuId = skuId
            self.modelId = modelId

    skus = []
    skus.append(sku('Triban RC520', 'https://www.decathlon.fr/p/velo-route-cyclotouriste-triban-rc520-frein-disque/', '2499491', '8502389'))
    skus.append(sku('Riverside 900 Gris anthracite / rouge vermillon fluo / Gris schist', 'https://www.decathlon.fr/p/velo-tout-chemin-riverside-900/', '2977706', '8577823'))
    skus.append(sku('Riverside 900 Gris anthracite / Menthe pastel / Gris pale', 'https://www.decathlon.fr/p/velo-tout-chemin-riverside-900/', '2985266', '8578872'))

    user_agent_list = [
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_5) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/13.1.1 Safari/605.1.15',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:77.0) Gecko/20100101 Firefox/77.0',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.97 Safari/537.36',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:77.0) Gecko/20100101 Firefox/77.0',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.97 Safari/537.36',
        'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:88.0) Gecko/20100101 Firefox/88.0'
    ]

    for isku in skus:
        print(isku.name)
        url = "https://www.decathlon.fr/fr/ajax/rest/model/com/decathlon/cube/commerce/inventory/InventoryActor/getStoreAvailability?storeIds=0070093300933%2C0070000200002%2C0070051800518%2C0070011800118%2C0070219902199%2C0070050400504%2C0070001500015%2C0070064800648%2C0070253902539%2C0070000100001&displayStoreDetails=false&skuId=" + isku.skuId + "&modelId=" + isku.modelId
        #print(url)
        reqOnline = urllib.request.Request(
            "https://www.decathlon.fr/fr/ajax/nfs/stocks/online?skuIds=" + isku.skuId,
            data=None, 
            headers={
                'User-Agent': random.choice(user_agent_list),
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                'Accept-Encoding': 'gzip, deflate, br',
                'Accept-Language': 'en-US,en;q=0.5',
                'Cache-Control': 'max-age=0',
                'Connection': 'keep-alive',
                'Host': 'www.decathlon.fr',
                'TE': 'Trailers',
                'Upgrade-Insecure-Requests': '1'
            }
        )
        response = urllib.request.urlopen(reqOnline)
        data = json.loads(response.read())    
        if data[isku.skuId]['stockOnline'] > 0:
            print('Found: ' + isku.url)
            message = client.messages \
                    .create(
                        body = isku.name + " dispo en ligne",
                        from_=twilio_from_number,
                        to=twilio_to_number
                    )
            found = True
        print(str(data[isku.skuId]['stockOnline']) + ' online')

        userAgent = random.choice(user_agent_list)

        req = urllib.request.Request(
            url, 
            data=None, 
            headers={
                'User-Agent': userAgent,
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                'Accept-Encoding': 'gzip, deflate, br',
                'Accept-Language': 'en-US,en;q=0.5',
                'Connection': 'keep-alive',
                'Host': 'www.decathlon.fr',
                'Upgrade-Insecure-Requests': '1'
            }
        )
        response = urllib.request.urlopen(req)
        cookies = response.getheader('Set-Cookie')
        
        req = urllib.request.Request(
            url, 
            data=None, 
            headers={
                'User-Agent': userAgent,
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                'Accept-Encoding': 'gzip, deflate, br',
                'Accept-Language': 'en-US,en;q=0.5',
                'Connection': 'keep-alive',
                'Host': 'www.decathlon.fr',
                'Upgrade-Insecure-Requests': '1',
                'Cookie': cookies
            }
        )

        if response.info().get('Content-Encoding') == 'gzip':
            data = gzip.decompress(response.read())
        elif response.info().get('Content-Encoding') == 'deflate':
            data = response.read()
        elif response.info().get('Content-Encoding'):
            print('Encoding type unknown')
        else:
            data = response.read()
        data = json.loads(data)
        for store in data['responseTO']['data']:
            if store['quantity'] > 0:
                print('Found: ' + isku.url)
                message = client.messages \
                    .create(
                        body = isku.name + " dispo à " + store['storeName'],
                        from_=twilio_from_number,
                        to=twilio_to_number
                    )
                found = True
            print(str(store['quantity']) + ' in ' + store['storeName'])
        time.sleep(5)
