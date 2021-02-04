import discord
from chatBot import Bot, botClient, adminBot

class MyClient(discord.Client):
    async def on_ready(self,AdminRoles=[]):
        print('Logged on as', self.user)
        self.uniBot=Bot("SUSSEXBOT") #set up once in the memory
        self.client=botClient(self.uniBot) #set up client in memory
        self.admin=adminBot(self.uniBot) #set up admin
        self.bots={}
        self.adminRoles=AdminRoles
        self.name="Bot test"
    async def on_message(self, message):
        #Assign a bot to each person
        if message.author == self.user:
            return
        found=False
        tag=""
        for i in message.mentions: #get all mentioned in the message
            if i.name == self.name: #if person has asked question
                found=True
                tag=i.name
        if found and not self.getAdmin(message): #if person has tagged bot
            mess=message.clean_content.replace("@"+self.name,"")
            print(mess)
            reply=self.client.Enter(mess).replace("$","")
            await message.channel.send("@"+message.author.name+" "+reply)
    def getAdmin(self,message):
        Pass=False
        try:
            roles=message.author.roles #gather the role of the user
            for i in roles:
                if str(i.name) in self.adminRoles: #don't answer these people
                    Pass=True
        except AttributeError: #if DM
            pass
        return Pass
client = MyClient()
client.run('Nzc2NDM5ODg0Njk2MTI1NDQw.X605_g.PgjL52BfYxYCcCP8HltHENIz6DY')
    

