# Telegram Google Places Bot



This Telegram Bot API helps users with finding the closest location of a specific type of locations (for example, restaurants, gas stations, pharmacoes, etc...) that the user inputs to the bot. The bot currently only operates on Telegram Mobile as location services are currently not available for Telegram Desktop. After the user visits the location, the user can input their personal rating of the location so that next time they are searching for a location they receive a personalized result, taking into account their rating in the proximitiy of such location, this is done using the following equation in the background (Distance x Rating/5).  

<img src="https://i.imgur.com/RlwcV0O.jpg" width="40%">.

# Setup

 - Install Telepot by entering the following command in the terminal:
`$ pip3 install telepot`
 - Create a Google Maps API and enable places and distances' APIs, store the API Key in a safe location. 
 - Install Google Maps by entering the following command in the terminal:
`$ pip3 install -U googlemaps`
  - Create a bot with BotFather. The instructions are in the following links.
 <https://www.instructables.com/id/Set-up-Telegram-Bot-on-Raspberry-Pi/>
<https://core.telegram.org/bots#6-botfather>

  - Create a config.json file with the following properties and replace the API key and token with yours. 
```
{
    "auth": {
        "Google_API_Key": "##########", 
        "Bot_Token": "##########"
    }
}
```

# Start 
`$ python3 ChatBot.py`
  

