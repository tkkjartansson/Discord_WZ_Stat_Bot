import mysql.connector
from datetime import datetime, timedelta
from dotenv import load_dotenv
import os

class DB_Interface:
    def __init__(self):
        load_dotenv()
        self.mydb = mysql.connector.connect(
            host=os.getenv('DB_WZ_STATS_HOST'),
            user=os.getenv('DB_WZ_STATS_USER'),
            password=os.getenv('DB_WZ_STATS_PASSWORD'),
            database=os.getenv('DB_WZ_STATS_DATABASE')
            )



    ###############
    #    ALIAS    #
    ###############



    # Input: 
    # {
    #       'DiscordName',
    #       'DiscordId'
    #       'PlayerName'
    #       'PlayerPlatform'
    # }


    def createUpdateAlias(self,aliasObject):
        cursor = self.mydb.cursor()

        userExistQueryString = "SELECT * FROM WZ_Alias WHERE DiscordId = %s"
        cursor.execute(userExistQueryString,(aliasObject['DiscordId'],))
        userExists = cursor.fetchone()

        if not userExists:
            createUserQueryString = "INSERT INTO WZ_Alias (DiscordName,DiscordId,PlayerName,PlayerPlatform) VALUES (%s,%s,%s,%s)"
            cursor.execute(createUserQueryString,(aliasObject['DiscordName'],aliasObject['DiscordId'],aliasObject['PlayerName'],aliasObject['PlayerPlatform']))
            self.mydb.commit()
        else:
            updateUserQueryString = "UPDATE WZ_Alias SET PlayerName = %s, PlayerPlatform = %s where id = %s"
            cursor.execute(updateUserQueryString,(aliasObject['PlayerName'],aliasObject['PlayerPlatform'],userExists[0]))
            self.mydb.commit()



    # Returns:
    # {
    #       'id'
    #       'DiscordName',
    #       'DiscordId'
    #       'PlayerName'
    #       'PlayerPlatform'
    # }

    def getAliasByDiscordId(self,discordId):
        cursor = self.mydb.cursor()

        queryString = "SELECT * from WZ_Alias WHERE DiscordId = %s"
        cursor.execute(queryString,(discordId,))
        userInfo = cursor.fetchone()

        if not userInfo:
            raise Exception('No Alias Found')

        return {
            'id'                : userInfo[0],
            'DiscordName'       : userInfo[1],
            'DiscordId'         : userInfo[2],
            'PlayerName'        : userInfo[3],
            'PlayerPlatform'    : userInfo[4]
        }



    ###############
    #    Stats    #
    ###############

    # Input:
    # {
    #       'PlayerName'
    #       'NumberOfGames'
    #       'Wins'
    #       'Kills'       
    #       'Deaths'
    #       'KD_Ratio'
    #       'Score_Per_Min'
    #       'CreatedOn'
    #       'WZ_Alias_Id'
    # }

    def createStatline(self, statLine):
        cursor = self.mydb.cursor()

        queryString = "INSERT INTO WZ_Stats (PlayerName,Number_Of_Games,Wins,Kills,Deaths,KD_Ratio,Score_Per_Min,CreatedOn,WZ_Alias_Id) Values (%s,%s,%s,%s,%s,%s,%s,%s,%s)"
        cursor.execute(queryString, (statLine['PlayerName'],statLine['NumberOfGames'],statLine['Wins'],statLine['Kills'],statLine['Deaths'],statLine['KD_Ratio'],statLine['Score_Per_Min'],statLine['CreatedOn'],statLine['WZ_Alias_Id']))
        self.mydb.commit()


    def getLatesStatLine(self, aliasId):
        cursor = self.mydb.cursor()

        queryString = "SELECT * from WZ_Stats WHERE WZ_Alias_Id = %s ORDER BY CreatedOn DESC LIMIT 1"

        cursor.execute(queryString,(aliasId,))

        statline = cursor.fetchone()

        if not statline:
            raise Exception('No stats found')

        return {
            'id'            : statline[0],
            'PlayerName'    : statline[1],
            'NumberOfGames' : statline[2],
            'Wins'          : statline[3],
            'Kills'         : statline[4],
            'Deaths'        : statline[5],
            'KD_Ratio'      : statline[6],
            'Score_Per_Min' : statline[7],
            'CreatedOn'     : statline[8],
            'WZ_Alias_Id'   : statline[9],
    }
   



