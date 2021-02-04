"""
* Artificial Intelligence chat bot framework
* Code developed by Dexter R Shepherd, aged 19
* Info found at shepai.github.io
* CB V0.0.2

UPDATES FROM PREVIOUS
*Better organization of data
*Faster search time
*Find more related data
"""

import json
from languageProcessor import LanguageProcessor as LP
import time
import os

LP=LP()
SYSTEM_PATHWAY=""
class ConfusedFile:
    #the confused file to store and count the unanswered items
    def __init__(self):
        try:
            file=open(SYSTEM_PATHWAY+"confused.json") #read file
            r=file.read()
            file.close()
            self.confused = json.loads(r) #convert to dictionary
        except:
            self.confused={}
    def add(self,item):
        #add item
        found=False
        for i in self.confused: #if similar questions don't add more
            if LP.get_similarity(i,item)>0.8:
                found=True
                self.confused[i]=self.confused[i]+1
                #break #pointless to keep looping
        if not found: #if it was not found
            self.confused[item]=1
        self.save()
    def retrieve(self,num=0):
        #retrieve items in priority order
        arr=[]
        pos=[]
        for i in self.confused: #sort into order
            insertion=False
            count=0
            while count<len(arr) and not insertion: 
                if pos[count]<self.confused[i]: #higher prob
                    arr.insert(count, i) #insert at position
                    pos.insert(count,self.confused[i])
                    insertion=True
                count+=1
            if not insertion: #if not inserted add to
                arr.append(i)
                pos.append(self.confused[i])
        if num>0 and len(arr)>num: #return if user specified length to return
            return arr[:num]
        else:
            return arr
    def remove(self,item):
        for i in self.confused.keys(): #if similar questions don't add more
            if LP.get_similarity(i,item)>0.8:
                self.confused.pop(i)#delete item
                break #pointless to keep looping
        self.save()
    def save(self):
        with open(SYSTEM_PATHWAY+"confused.json", 'w', encoding='utf-8') as f:
            json.dump(self.confused, f)
class logFile:
    def __init__(self,name=""):
        if not os.path.isdir("infoFiles/"):
            os.mkdir("infoFiles/") #set aside area for logFiles
        if name!="":
            self.name=name
            #open file
            try:
                file=open(SYSTEM_PATHWAY+"infoFiles/"+self.name+".json") #read file
                r=file.read()
                file.close()
                self.convo = json.loads(r) #convert to dictionary
            except: #if file not existant
                self.convo={}
        else:
            raise ValueError ("Name is empty, try naming it as a topic")
    def delete(self,item):
        Types=self.getType(item)
        ans,p=self.getAnswer(item)
        if ans!="" and p!=0: #check it is in there
            try:
                for Type in Types:
                    self.convo[Type].pop(item) #delete
            except KeyError:
                pass
        self.save()
    def add(self,item,answer,timeLimit=[]):
        #organize via sentence structure
        #if information or similar is not yet in file add it
        #store in style {structure_type:{question:[answer]}}
        Types=self.getType(item)
        for Type in Types:
            items=self.convo.get(Type,None) #find connected in structure
            if items!=None:
                answer1,prob=self.getAnswer(item) #get the current answer
                if (answer1=="" and prob==0) or (item not in self.convo[Type] and prob<0.8) : #needs adding or needs replacing
                    self.convo[Type][item]=[answer]+timeLimit #set
            else:
                self.convo[Type]={item:[answer]+timeLimit}
        self.save() #save
    def getAnswer(self,item):
        #find the most likely and return it if it is likely enough and within the time limit if given
        Types=self.getType(item)
        current=0
        save=""
        for Type in Types:
            items=self.convo.get(Type,None) #find connected in structure
            if items!=None:
                for i in items: #loop through all items in this category
                    score=LP.get_similarity(i,item) #find the score
                    if score > current: #get the largest
                        current = score
                        save=i
        if save!="" and current!=0: #if found something
            return self.convo[Type][save][0], current #return it as answer and probability
        return "", 0 #return nothing
    def getType(self,item):
        #get the meaning of the item and return the tag to store it under
        subs=LP.split_meaning(item,Type='subjects',tags=True)
        #count the occurances to find the most dominant tag, if multiple then pick w over v
        if len(subs)==0:
            subs=["noSub"]
        return subs
    def save(self):
        with open(SYSTEM_PATHWAY+"infoFiles/"+self.name+".json", 'w', encoding='utf-8') as f:
            json.dump(self.convo, f)
class Bot:
    #main chatbot code to bind together the language and memory
    def __init__(self,name,systemPath=""):
        #enter the system path that the data will be deployed
        self.name=name
        self.systemPath=systemPath
        SYSTEM_PATHWAY=systemPath #set the global
        try:
            file=open(SYSTEM_PATHWAY+"topics.json") #read file
            r=file.read()
            file.close()
            self.topics = json.loads(r) #convert to dictionary
        except:
            self.topics={} #store each topic
        self.confused=ConfusedFile()
        try:
            file=open(SYSTEM_PATHWAY+"reports.json") #read file
            r=file.read()
            file.close()
            self.reports = json.loads(r) #convert to dictionary
        except:
            self.reports={} #store each topic and the log file related
    def chat(self,message):
        #get a response
        topics=LP.get_frequent_topics(message)#find the topics dominant
        if topics==[]: #if none found
            topics=["entity"]
        #find log files related to the topics
        logs=[]
        for i in topics: #get all logfiles
            logs+=self.topics.get(i,[])
            if self.topics.get(i,[]) == []: self.topics[i]=[i]
        pass #remove duplicates
        #find the potential answers and their probabilities
        top=0
        saved=""
        if logs!=[]:
            for i in topics:
                log=logFile(name=i)
                answer,prob=log.getAnswer(message)
                if prob>top: #save the highest probability
                    top=prob
                    saved=answer
            if top>0.8:
                return saved#return most likely
            elif top>0.5: #if under threshold return the maybes
                return "This is something similar I found which may answer your question '"+saved+"'"
        else:
            for i in topics: #add topics and log files to the system
                log=logFile(name=i)
                items=self.topics.get(i,[])
                items.append(log.name)
                self.topics[i]=items
            self.save()
        self.confused.add(message) #add to be answered
        return "Sorry, I am not sure on that yet. Maybe ask again another time and you will get your answer"#return unknown message
    def add(self,message,response,time=[]):
        #allow the application to add information
        topics=LP.get_frequent_topics(message)#find the topics dominant
        if topics==[]: #if none found
            topics=["entity"]
        logs=[]
        for i in topics: #get all logfiles
            logs+=self.topics.get(i,[])
        if logs==[]:
            for i in topics: #add topics and log files to the system
                log=logFile(name=i)
                items=self.topics.get(i,[])
                if log.name not in items:
                    items.append(log.name)
                self.topics[i]=items
        for log in topics:
            log=logFile(name=log)
            log.add(message,response,timeLimit=time)
        self.save()
    def delete(self,message):
        topics=LP.get_frequent_topics(message)#find the topics dominant
        if topics==[]: #if none found
            topics=["entity"]
        logs=[]
        for i in topics: #get all logfiles
            logs+=self.topics.get(i,[])
        
        for log in logs:
            log=logFile(name=log)
            log.delete(message)
        self.save()
    def report(self,message):
        #if the user reports a message to be reviewed
        self.reports[message]=self.reports.get(message,0)+1
        self.save()
    def save(self):
        with open(SYSTEM_PATHWAY+"topics"+".json", 'w', encoding='utf-8') as f:
            json.dump(self.topics, f)
        with open(SYSTEM_PATHWAY+"reports"+".json", 'w', encoding='utf-8') as f:
            json.dump(self.reports, f)
class botClient:
    #built to use less memory and provide an interface with the main bot
    #responsible for interacting
    def __init__(self,bot):
        self.bot=bot
    def Enter(self,userinput):
        userinput=userinput.replace("$","dollars")
        if userinput!="":
            sentence=userinput.replace("?",".").replace("!",".").replace(";",".") #split sentences
            sentences=sentence.split(".")
            sentences=[x for x in sentences if x]
            responses=""
            for sentence in sentences: #loop through multiple sentences
                returned=self.bot.chat(sentence)
                if returned == "Sorry, I am not sure on that yet. Maybe ask again another time and you will get your answer":
                    #there was nothing in the data
                    responses=returned
                    break
                responses+=returned+"$"
            return responses
        return ""
    def feedback(self,type,sentence):
        if type=="negative":
            self.bot.confused.add(sentence)
    def report(self,question):
        #report the data to the admin
        self.bot.report(question)
    def add(self,question,answer):
        #allow the user to add through positive feedback
        t=[]#get current time if existant
        self.bot.add(question,answer,time=t)
        self.bot.confused.remove(question)
class adminBot:
    #built to use less memory and provide an interface with the main bot
    #responsible for teaching and managing
    def __init__(self,bot):
        self.bot=bot
    def getToAdd(self):
        return self.bot.confused.retrieve()
    def add(self,question,answer,t=[]):
        #allow the user to add through positive feedback
        self.bot.add(question,answer,time=t)
        self.bot.confused.remove(question)
    def delete(self,question): #delete a confused question
        self.bot.confused.remove(question)
    def deleteQ(self,question): #delete a question and its answers
        self.bot.delete(question)
        return True
    def getReport(self):
        reported=list(self.bot.reports.keys())
        arr=[]
        length=0
        for i in reported: #convert to array
            if length+len(i)>400: break #break
            arr.append(i)
            length+=len(i)
        return arr
    def addConfused(self,sentence):
        self.bot.confused.add(sentence)
    def deleteReport(self,sentence):
        self.bot.reports.pop(sentence)
