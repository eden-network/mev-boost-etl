import requests
import json
import os
import time
relays=[
{"id":"eden","url":"https://relay.edennetwork.io/relay/v1/data/bidtraces/proposer_payload_delivered?limit=100"},
{"id":"relayoor","url":"https://relayooor.wtf/relay/v1/data/bidtraces/proposer_payload_delivered?limit=100"},
{"id":"manifold","url":"https://mainnet-relay.securerpc.com/relay/v1/data/bidtraces/proposer_payload_delivered?limit=100"},
{"id":"flashbots","url":"https://boost-relay.flashbots.net/relay/v1/data/bidtraces/proposer_payload_delivered?limit=100"},
{"id":"blocknative","url":"https://builder-relay-mainnet.blocknative.com/relay/v1/data/bidtraces/proposer_payload_delivered?limit=100"},
{"id":"bloxrouteMaxProfit","url":"https://bloxroute.max-profit.blxrbdn.com/relay/v1/data/bidtraces/proposer_payload_delivered?limit=100"},
{"id":"bloxrouteEthical","url":"https://bloxroute.ethical.blxrbdn.com/relay/v1/data/bidtraces/proposer_payload_delivered?limit=100"},
{"id":"bloxrouteRegulated","url":"https://bloxroute.regulated.blxrbdn.com/relay/v1/data/bidtraces/proposer_payload_delivered?limit=100"},
{"id":"agnostic","url":"https://agnostic-relay.net/relay/v1/data/bidtraces/proposer_payload_delivered?limit=100"},
{"id":"ultrasound","url":"https://relay.ultrasound.money/relay/v1/data/bidtraces/proposer_payload_delivered?limit=100"},
{"id":"aestus","url":"https://mainnet.aestus.live/relay/v1/data/bidtraces/proposer_payload_delivered?limit=100"}
]
latestSlotStored=7171966-10 # TO-DO should be parsed from bigquery table, initially 0 as we parse from the start
startSlot = latestSlotStored
def getRelayData(id,url,cursor):
    global startSlot
    if (cursor=="latest"):
        url=url
    else:
        url=url+"&cursor="+str(cursor)
    try:
      x = requests.get(url)
      y = json.loads(x.text)
      for slot in y:
          json_object = json.dumps(slot)
          if (os.path.exists("relayData/"+str(slot["slot"])+"_"+id+".json")):
              return "0"
          elif (int(slot["slot"])<startSlot):
              return "0"
          else:
            with open("relayData/"+str(slot["slot"])+"_"+id+".json", "w") as outfile:
                outfile.write(json_object) #Writing file as json, needs to be modified so it will write to a csv and dump to BigQuery
            returnCursor=slot["slot"]
      return (int(returnCursor)-1)
    except Exception as e:
      print(e)
      return "ERR"
def relayUpdater():
    for relay in relays:
        id= relay["id"]
        url= relay["url"]
        cursor= "latest"
        while (cursor!="0"):
            cursor=getRelayData(id,url,cursor)
            time.sleep(1) #relays have rate limits so we need to wait 1 seconds between requests 
            print (cursor)
            if (cursor=="ERR"):
                print ("error on relay: "+str(id))
                break

relayUpdater()