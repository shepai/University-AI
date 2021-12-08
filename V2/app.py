#application layer
import asyncio
import websockets
from chatBot import Bot, botClient, adminBot
import copy
import json
#"/var/www/html/"
uniBot=Bot("SUSSEXBOT") #set up once in the memory
client=botClient(uniBot) #set up client in memory
admin=adminBot(uniBot) #set up admin
Admins=[]
#file=open("/home/shep/Desktop/pw.txt","r") #store codes here
#r=file.read()
#file.close()
#codes=r.split("-")
codes=["",""]
orgs={}
def save(self,orgs):
    with open("organisation.json", 'w', encoding='utf-8') as f:
        json.dump(orgs, f)
try:
    file=open("organisation.json") #read file
    r=file.read()
    file.close()
    tmp = json.loads(r) #convert to dictionary
    for key in tmp:
        orgs[key]=copy.deepcopy(Bot(key)) #create all objects
except:
    pass
#on server ths is shepadmin-pass
print("opening server")
async def clientReply(websocket, path):
    try:
        async for message in websocket:
            #will need to split down
            parts=message.split("-+-+") #code to split org and codes
            message=parts[1]
            organisation=parts[0]
            if orgs.get(organisation,None)!=None: #validate organisation
                uniBot=orgs[organisation]
                client=botClient(uniBot) #set up client in memory
                admin=adminBot(uniBot) #set up admin
                if "FEEDBACKN" in message: #negative feedback add sentence to confused
                    client.feedback("negative",message.replace("FEEDBACKN",""))
                elif "FEEDBACKP" in message:
                    a=message.replace("FEEDBACKP","").split("---")
                    print("Add",a[0],a[1])
                    client.add(a[0],a[1])
                elif "REPORT" in message:
                    print("report")
                    client.report(message.replace("REPORT",""))
                else:
                    print("RECIEVED:",message)
                    message=message.split("---")
                    arr=[]
                    for i in message[1].split(","):
                        arr.append(i)
                    x=client.Enter(message[0])
                    await websocket.send(x+"---")
    except websockets.exceptions.ConnectionClosedError:
            print("User disconnected")
async def adminReply(websocket, path):
    print("admin")
    try:
        async for message in websocket:
            #will need to split down
            if "signInRequest:" in message:
                #sign in
                message=message.replace("signInRequest:","")
                message=message.split("--")
                if message[0]==codes[0] and message[1]==codes[1]:
                    print(websocket,"has joined the administration")
                    Admins.append(websocket)
                    await websocket.send("signInRequestGranted")
                else:
                    await websocket.send("ERROR")
            elif message=="VIEWDATA" and websocket in Admins:
                print("view")
                #return the data
                string=""
                d=admin.getToAdd()
                for i in d:
                    string+=i+":::"
                    if len(string)>500: #prevent websocket error
                        break
                print(string[:-3])
                await websocket.send(string[:-3]) #send list of to add
            elif "RADD" in message and websocket in Admins:
                #add for reporting
                a=message.replace("RADD","")
                a=a.split("---")
                admin.deleteReport(a[0]) #delete from report
                admin.deleteQ(a[0]) #delete from memory
                admin.add(a[0],a[1]) #add to the bot
            elif "QADD" in message and websocket in Admins:
                #add a question back using undo method
                admin.addConfused(message.replace("QADD",""))
            elif "ADD" in message and websocket in Admins:
                print("add",message.replace("ADD",""))
                a=message.replace("ADD","")
                a=a.split("---")
                if a[2]=="":
                    admin.add(a[0],a[1]) #add to the bot
                else:
                    admin.add(a[0],a[1],t=[a[2]]) #add to the bot
            elif "DELETER" in message and websocket in Admins:
                admin.deleteReport(message.replace("DELETER",""))
            elif "DELETE" in message and websocket in Admins:
                admin.delete(message.replace("DELETE",""))
            elif "DELQUE" in message and websocket in Admins:
                print("delete",message.replace("DELQUE",""))
                val=admin.deleteQ(message.replace("DELQUE",""))
                if val==None:
                    await websocket.send("ERROR")
            elif "REPORT" in message and websocket in Admins:
                string=""
                d=admin.getReport()
                for i in d:
                    string+=i+":::"
                await websocket.send(string[:-3]) #send list of to add
    except websockets.exceptions.ConnectionClosedError:
            print("remove admin", websocket)
            del Admins[Admins.index(websocket)]

async def assign(websocket, path):
    try:
        async for message in websocket:
            #will need to split down
            print("RECIEVED:",message)
            if message=="LIST":
                str=""
                for item in orgs:
                    str+=item+":::"
                await websocket.send(">>>"+str)
            elif "ADD" in message:
                message=message.remove("ADD")
                if message not in list(orgs.keys()):
                    uniBot=Bot(message) #set up in memory
                    orgs[message]=copy.deepcopy(uniBot)
                    save(orgs)
                    await websockets.send("Success")
                else:
                    await websocket.send("Already signed up")
    except websockets.exceptions.ConnectionClosedError:
        print("User disconnected")
asyncio.get_event_loop().run_until_complete(
websockets.serve(clientReply, port=50007)) #listen for clients
asyncio.get_event_loop().run_until_complete(
websockets.serve(adminReply, port=8080)) #listen for clients
asyncio.get_event_loop().run_until_complete(
websockets.serve(assign, port=4040)) #listen for clients
asyncio.get_event_loop().run_forever()
