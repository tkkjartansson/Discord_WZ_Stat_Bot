import requests
import urllib.parse
import json
from dotenv import load_dotenv
import os

class API_Interface:

    def __init__(self):
        load_dotenv()
        self.rapidAPIKey = os.getenv('RAPID_API_KEY')

    def getPlayerStats(self,playerName,playerPlatform):
        playerNameHTML = urllib.parse.quote(playerName)
        url = f"https://call-of-duty-modern-warfare.p.rapidapi.com/warzone/{playerNameHTML}/{playerPlatform}"
        header = {
            'x-rapidapi-key' : self.rapidAPIKey
        }

        r = requests.get(url=url,headers=header)
        #Hack to see if there is an error since the status code is 200 even though the inputs don't match a user
        if(r.status_code != 200 or r.text.find('error') != -1):
            raise Exception('Error with the API. Try re-creating your Alias')
        else:
            response_dict = json.loads(r.text)
            return response_dict['br']

    def getWeeklyStats(self,playerName,playerPlatform):
        playerNameHTML = urllib.parse.quote(playerName)
        url=f"https://call-of-duty-modern-warfare.p.rapidapi.com/weekly-stats/{playerNameHTML}/{playerPlatform}"
        header = {
            'x-rapidapi-key' : self.rapidAPIKey
        }

        r = requests.get(url=url,headers=header)
        #Hack to see if there is an error since the status code is 200 even though the inputs don't match a user
        if(r.status_code != 200 or r.text.find('error') != -1):
            raise Exception('Error with the API. Try re-creating your Alias')
        else:
            response_dict = json.loads(r.text)
            return response_dict['wz']['all']['properties']
        

        