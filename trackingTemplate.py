import csv
import os
import datetime as time
from numpy import array
from regex import D
import requests
from bs4 import BeautifulSoup
import re
from twitterAPItest import bearer_oauth, connect_to_endpoint

'''
    This project creates a multidimensional tracking metrics with trading and social data
    The final output is a csv file and each run updates the newest data
    Full csv header if all modules are used is:
        Date, Token_Price, Circulating_Supply, Circulating%, Mcap, Hodler, Hodler_Growth%, Twitter_Follower, Discord_User, Discord_User_Growth%, Telegram_user
'''

class trackingTemplate():
    def __init__(self, name) -> None:
        '''
            :param addr[]: array of token addresses - this is 
            :param tokenName: array of the names of all tokens of the project
        '''
        self.projectName = name
        
        #initialize csv header list
        self.header = ["Date"]
        #initialize corresponding data list
        self.data = [time.datetime.now().strftime("%Y-%m-%d")]
 
    def marketData(self, tokenName):
        '''
            Get token price, circulating supply, Circulation%, mcap
            from CoinGecko
            : param tokenName: token name of the project - tricky because coinGecko gives tokens different names- GMT is named stepn and GST is named green-satoshi-token... weird af
            : return: 1- all data added into self.data successfully, warning - missing data
        '''
        #set up coinGecko api
        url = "https://api.coingecko.com/api/v3/coins/{}?localization=false&tickers=false&market_data=true&community_data=true&developer_data=true&sparkline=true"
        try:
            response = requests.get(url.format(tokenName)).json()
        except:
            print("An exception occurred when fetching coinGecko data")
        # price is the 24hr highest
        tokenPrice = response["market_data"]["high_24h"]["usd"]
        circulatingSupply = response["market_data"]["circulating_supply"]
        totalSupply = response["market_data"]["total_supply"]
        circulationP = circulatingSupply/totalSupply
        mcap = totalSupply*tokenPrice
        return tokenPrice, circulatingSupply, circulationP, mcap
    
    
    def hodlerData(self,tokenAddr):
        '''
            Get holder count then calculate percentage increase
            from __scan - demo with solscan
            : param tokenName: token address of the project - crucial as token symbol is not unique
            : return: totalHodler
            print warning - missing data
        '''
        #set up solscan api
        url = "https://public-api.solscan.io/token/holders?tokenAddress={}&offset=0&limit=1"
        
        try:
            response = result = requests.get(url.format(tokenAddr)).json()
        except:
            print("An exception occurred when fetching hodler data")
        totalHodler = response["total"]
        return totalHodler
    
    

    def twitterFol(self,bearer_token, usernames):
        '''
            This function gets the follower count from Twitter
            : param: bearer_token - set up your twitter dev account and fetch the bearer token
            : param: usernames = Specify the usernames that you want to lookup below
                                 You can enter up to 100 comma-separated values.
            : return: follwerCount
        '''
        #bearer_token = "AAAAAAAAAAAAAAAAAAAAALPMcAEAAAAAOIg1pxrBcVshtZX7XV2yq6WTC08%3DioqoXMQbulkr5ePUuNsB7J9v7zwsEYylUFYsgt5Ghtx4TE9Oxf"
        # usernames = "usernames=yanffyy"
        url = "https://api.twitter.com/2/users/by?usernames={}&user.fields=public_metrics".format(usernames)
        json_response = connect_to_endpoint(url)
        followerCount = int(json_response["data"][0]["public_metrics"]["followers_count"])
        return followerCount


    def discordFol(self,url):
        '''
            This function gets the follower count from Discord
            : param: url - Discord invite link
            : return: memberCount
        '''
        # url = 'https://discord.com/invite/stepn'
        source = requests.get(url).text
        soup = BeautifulSoup(source, features="html.parser")
        # get server description where member count is contained
        dc = soup.find("meta", attrs={'property': 'og:description'})
        # use regex to parse out 4 words before the target word "members"
        r1 = re.search(r"(?:[a-zA-Z'-]+[^a-zA-Z'-]+){0,3}members", str(dc))
        # find the word that start with number in the 4 words before target word "members"
        b = [str(s) for s in r1.group().split() if s[0].isdigit()]
        # turn str into int
        memberCount = int(b[0].replace(",", ""))
        return memberCount
    
    
    def telegramFol(self,url):
        '''
            This function gets the follower count from Twitter
            : param: url - telegram invite link
            : return: memberCount
        '''
        #url = "https://t.me/traderjoe_xyz"
        headers = {
                    'user-agent': 'User-Agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.127 Safari/537.36'
                }
        response_1 = requests.get(url=url, headers=headers)
        soup_1 = BeautifulSoup(response_1.text, 'html.parser')

        try:
            rawMemberCount = soup_1.find("div",attrs={"class":"tgme_page_extra"}).text
            memberCount = int(rawMemberCount.split("members")[0].replace(" ", ""))
        except:
            memberCount = None
            pass
        
        return memberCount


    def csvOutput(self, row, header =[], placeholder = []):
        #check if file exists in CURRENT directory
        fileExists = os.path.exists(self.projectName+'.csv')
        #update existing
        if fileExists:
            print("add to last row")
            #  get last line of the csv file- yesterday's data
            with open(self.projectName+".csv", "r", encoding="utf-8", errors="ignore") as f:
                final_line = f.readlines()[-1] # this is a string
                final_line_parsed = final_line.split(",")
                # update the row
                lastGSTHolderCount = int(final_line_parsed[placeholder[0]-1])
                row[placeholder[0]] = round((row[placeholder[0]-1]/lastGSTHolderCount -1) *100,2)
                lastGMTHolderCount = int(final_line_parsed[placeholder[1]-1])
                row[placeholder[1]] = round((row[placeholder[1]-1]/lastGMTHolderCount -1) *100,2)
                lastDiscordCount = int(final_line_parsed[placeholder[2]-1])
                row[placeholder[2]] = round((row[placeholder[2]-1]/lastDiscordCount -1) *100,2)
                f.close()
            #write in 
            with open(self.projectName+".csv","a+",newline="") as f: 
                # add into file
                f_csv = csv.writer(f)
                f_csv.writerow(row)

        #create if not existing
        else:
            # first time setup
            with open(self.projectName+".csv","w") as f:
                f_csv = csv.writer(f)
                f_csv.writerow(header)
                f_csv.writerow(row)


# create instance
sample = trackingTemplate("Stepn")
# get composable data
gmttokenPrice, gmtcirculatingSupply, gmtcirculationP, gmtmcap = sample.marketData("stepn")
gmtcirculatingSupply = round(gmtcirculatingSupply,0)
gmtcirculationP = round(gmtcirculationP,2)*100
gmtmcap = round(gmtmcap,2)
gsttokenPrice, gstcirculatingSupply, gstcirculationP, gstmcap = sample.marketData("green-satoshi-token")
gstcirculatingSupply = round(gstcirculatingSupply,0)
gstcirculationP = round(gstcirculationP,2)*100
gstmcap = round(gstmcap,2)
gmtTotalHodler = sample.hodlerData("7i5KKsX2weiTkry7jA4ZwSuXGhs5eJBEjY8vVxR4pfRx")
gstTotalHodler = sample.hodlerData("AFbX8oGjGpmVFywbVouvhQSRmiW2aR1mohfahi4Y2AdB")
twitter = sample.twitterFol("AAAAAAAAAAAAAAAAAAAAALPMcAEAAAAAOIg1pxrBcVshtZX7XV2yq6WTC08%3DioqoXMQbulkr5ePUuNsB7J9v7zwsEYylUFYsgt5Ghtx4TE9Oxf", "Stepnofficial")
discord = sample.discordFol("https://discord.com/invite/stepn")
telegram = sample.telegramFol("https://t.me/STEPNofficial")

# create header if first time setup the project file
addHeader = ["GST_Token_Price", "GST_Circulating_Supply", "GST_Circulating%", "GST_Mcap", "GST_Hodler", "GST_Hodler_Growth%", "GMT_Token_Price", "GMT_Circulating_Supply", "GMT_Circulating%", "GMT_Mcap", "GMT_Hodler", "GMT_Hodler_Growth%", "Twitter_Follower", "Discord_User", "Discord_User_Growth%", "Telegram_user"]
header = sample.header+addHeader

# create the output - append to existing file or open a new one if not yet created
# if you choose to open a new one, please input the desired header array otherwize would be empty by default
# in addition, for growth% that relies on the calculation of previous days, leave it in blank - "/"
'''
addData = [gsttokenPrice, gstcirculatingSupply, gstcirculationP, gstmcap, gstTotalHodler,"/",gmttokenPrice, gmtcirculatingSupply, gmtcirculationP, gmtmcap, gmtTotalHodler,"/",twitter,discord,"/",telegram]
row = sample.data+addData
print(row)
sample.csvOutput(row,header = header)
'''

# update exisitng file
# we need to calculate growth% based on previous data, therefore, carefully put in placeholder in row and its corresponding indexes in the placeholder array
placeholder = [6,12,15]
addData = [gsttokenPrice, gstcirculatingSupply, gstcirculationP, gstmcap, gstTotalHodler,placeholder,gmttokenPrice, gmtcirculatingSupply, gmtcirculationP, gmtmcap, gmtTotalHodler,placeholder,twitter,discord,placeholder,telegram]
row = sample.data+addData
#print(row)
sample.csvOutput(row,placeholder = placeholder)