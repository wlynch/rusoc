#!/usr/bin/env python

import json, httplib, sys, webbrowser, traceback
from commands import getoutput

#Written by Billy Lynch <wlynch92@cs.rutgers.edu>
#June 2012

#Error codes:
#0 : Success
#1 : Failure (section closed)
#2 : Invalid input/arguments
#3 : No response (class/subject does not exist)
#4 : No Internet Connection

#TODO
#1) Find a way to have a decent ldap system.
#   Is there a way to map the rulinkRutgersEduOrganizationCode with a department?
#2) list individual classes instead of department for simple format output (perfect for bashrc)
#   Change function so header only appears once for each subject

#Global Variables
#Default (current) semester. Must currently be set manually.
semester="12013"


#Recursive print of the dictionary (covers sub-dictionaries such as sections)
def printDict(dict,tab):
    for key in dict.keys():
        i=0
        while (i<tab):
            print('\t'),
            i+=1
        print(key+" : "),
        if (type(dict[key]) is list):
            if (len(dict[key])>0):
                #print(dict[key][0])
                print
                for sect in dict[key]:
                    printDict(sect,tab+1)
            else:
                print('None')
        #elif (dict[key]) is None):
        #    print
    else:
        print(dict[key])
    print

#Simple linear search for the course. Dump all the info to stdout.
def searchCourseNum(dict, course):
    x=0
    while (x<len(dict)):
        if (dict[x]['courseNumber'] == course):
            printDict(dict[x],0)
            return 0
        x+=1
    exit(3) 

#Simple linear search for the course. Dump all the info to stdout.
def getJSON(dict, course):
    x=0
    while (x<len(dict)):
        if (dict[x]['courseNumber'] == course):
            print dict[x];
            return 0
        x+=1
    exit(3) 

# Go through each class, print courseNum, class name, and num sections open
def listAllCourses(dict, subject):
    x=0
    while (x<len(dict)):
        print(dict[x]['courseNumber']),
        print(" : "),
        print(dict[x]['title']),
        print("\t: "),
        total=0
        open=0
        #Determine number of 
        while (total<len(dict[x]['sections'])):
            if (dict[x]['sections'][total]['openStatus']):
                open+=1
            total+=1
        print(str(open)+"/"+str(total)+" sections open")
        x+=1
def listCourse(dict, subject, course):
    x=0
    while (x<len(dict)):
        if (dict[x]['courseNumber'] == course):
            print(dict[x]['courseNumber']),
            print(" : "),
            print(dict[x]['title']),
            print("\t: "),
            total=0
            open=0
            while (total<len(dict[x]['sections'])):
                if (dict[x]['sections'][total]['openStatus']):
                    open+=1
                total+=1
            print(str(open)+"/"+str(total)+" sections open")
            break
        x+=1
def isOpen(dict,course,section):
    x=0
    retval=True
    while (x<len(dict)):
        if (dict[x]['courseNumber']==course):
            y=0
            while (y<len(dict[x]['sections'])):
                if (section=="0" or section == dict[x]['sections'][y]['number']):
                    if (dict[x]['sections'][y]['openStatus']):
                        print(dict[x]['title']+" Section "+dict[x]['sections'][y]['number']+" is OPEN")
                    else:
                        print(dict[x]['title']+" Section "+dict[x]['sections'][y]['number']+" is CLOSED")
                        retval=False
                    if (section!="0"):
                        return retval
                y+=1
        x+=1
    return False 

#Open webreg in default webbrowser
def openWebReg(indexes):
    url="https://sims.rutgers.edu/webreg/editSchedule.htm?login=cas&semesterSelection="+semester+"&indexList="
    temp=0
    for index in indexes:
        if (temp!=0):
            url+=","
        temp=1
        url+=index
    print(url)
    webbrowser.open_new_tab(url)


#! Need to change these functions to binary search

def getCourse(dict,course):
    if (dict==[]):
        return None
    x=0
    while(x<len(dict)):
        if (dict[x]['courseNumber']==course):
            return dict[x]
        x+=1


def getValue(dict,course,key):
    if (dict==[]):
        return ""
    x=0
    while(x<len(dict)):
        if (dict[x]['courseNumber']==course):
            return dict[x][key]
        x+=1

def getSectionValue(dict,course,section,key):
    if (dict==[]):
        return ""
    x=0
    while(x<len(dict)):
        if (dict[x]['courseNumber']==course):
            y=0
            while(y<len(dict[x]['sections'])):
                if (dict[x]['sections'][y]['number']==section):
                    return dict[x]['sections'][y][key]
                y+=1
        x+=1

def getEmail(dict,courseNum,section):
    course=getCourse(dict,courseNum)
    oldProf=""
    rawName=""
    for sections in course['sections']:
        if (sections['number']==section):
            if (len(sections['instructors'])>0):
                rawName=sections['instructors'][0]['name']
                break
        else:        
            if (len(sections['instructors'])>0):
                rawName=sections['instructors'][0]['name']
    name=rawName.split(', ')
    query="ldapsearch -LLL -h ldap.rutgers.edu -p 389 -x -b \"dc=rutgers,dc=edu\" \"(&(sn="+name[0]+")(givenName="+name[1]+"*))\" cn mail 2>/dev/null | grep -v dn:"
    output=getoutput(query).split('\n')
    print(output)
    for line in output:
        print(line.strip())

#Get subject name from number
def getSubjectName(dict,subject):
    if (dict==[]):
        return ""
    for x in range(len(dict)):    
        if (dict[x]['code']==subject):
            return dict[x]['description']

def loadSubjectDict(semester):
    url="/soc/subjects.json?semester="+semester+"&campus=NB&level=U"
    try:
        conn = httplib.HTTPConnection("sis.rutgers.edu")
        conn.request("GET",url)
        resp = conn.getresponse()
        return json.loads(resp.read())
    except:
        exit(0);

def loadDict(subject,semester):
    url="/soc/courses.json?subject="+str(subject)+"&semester="+semester+"&campus=NB&level=U"
    conn = httplib.HTTPConnection("sis.rutgers.edu")
    conn.request("GET",url)
    resp = conn.getresponse()
    return json.loads(resp.read())

#Not really need. Can replace with getValue
def getNumSections(dict,course):
    x=0
    while (x<len(dict)):
        if (dict[x]['courseNumber']==course):
            return len(dict[x]['sections'])
        x+=1

def printInfo(dict,courseNum,selectedSection):
    course=getCourse(dict,courseNum)
    print(course['offeringUnitCode']+":"+course['subject']+":"+course['courseNumber']+" - "+course['title'])
    print("Sections: "+str(len(course['sections'])))
    oldInstruct="None"
    for sectionNum in range(len(course['sections'])):
        if (selectedSection=="0" or selectedSection==course['sections'][sectionNum]['number']):
            section=course['sections'][sectionNum]
            #print("Section "+str(sectionNum+1)+")"),
            print("Section "+section['number']+")"),
            if (section['openStatus']):
                print("\t[OPEN]")
            else:
                print("\t[CLOSED]")
            print("\tIndex: "+str(section['index']))
            print("\tInstructors:")
            if (section['instructors']==[]):
                print("\t\t"+oldInstruct)
            else:
                for instructor in section['instructors']:
                    print("\t\t"+instructor['name'])
                    oldInstruct=instructor['name']
            for location in section['meetingTimes']:
                if (location['meetingModeDesc']=="HYBRID SECTION" or location['meetingModeDesc']=="ONLINE INSTRUCTION(INTERNET)"):
                    print("\t"+location['meetingModeDesc'])
                else:
                    print("\t"+location['meetingModeDesc']+" : "+location['meetingDay']+" "+location['startTime']+""+location['pmCode']+"-"+location['endTime'])
                    print("\t\t"+location['campusName']+" : "+location['buildingCode']+" "+location['roomNumber'])
            print

#Help method.
def help():
    print('help')
    print("Usage: \t python parse.py <action> <args>")
    print("Summary:")
    print("\tinfo <subject>:<course>[#<section>] [<subject>:<course>[#<section>]] ...")
    print("\t\tList information about each class/section")
    print("\tlist <subject> [<subject>] ...")
    print("\tisOpen <subject>:<course>[#<section>] [<subject>:<course>[#<section>]] ...")
    print("\tregister <subject>:<course>[#<section>] [<subject>:<course>[#section>]] ...")
    print("\tdump")

#MAIN

#Possible operations:
#info <course num> [<semester>]
#search <string> [<semester>]
#list <major> [<semester>]

if (len(sys.argv) <= 2):
    help()
    exit(2)

commands=["list","info","search","isOpen","register","email","dump","json"]
if (commands.count(sys.argv[1])==0):
    help()
    exit(2)

#Load subject dictionary
subDict=loadSubjectDict(semester)


#Some initial temp/counter variables
oldSubject=0
retval=0
i=2
register=[]
first=True

while (i < len(sys.argv)):
    course=0
    try:
        input=sys.argv[i].split('#')
        if (len(input)>1):
            #section=int(input[1])
            if (input[1].isdigit()):
                if (int(input[1])<10):
                    if (int(input[1])==0):
                        section="0"
                    else:
                        section="0"+str(int(input[1]))
                else:
                    section=input[1]
            else:
                section=input[1].upper()
#            print(section)
        else:
            section="0"
        #Get subject number
        courseNum=input[0].split(':')
        subject=courseNum[len(courseNum)-2]
        if (len(courseNum) > 1):
            course=courseNum[len(courseNum)-1]

        if (subject!=oldSubject):
            #print("load dict")
            #Retrieve and load JSON into dict
            dict =  loadDict(subject,semester)
        if (dict==[]):
            #Empty dictionary
            retval=3 
        #Switch on option given
        if (sys.argv[1]=="list"):
            if (i>2 and subject!=oldSubject):
                print
            if (first or subject!=oldSubject):
                print("Subject: "+str(subject)+" - "+getSubjectName(subDict,subject))
                first=False
            if (course==0):
                listAllCourses(dict,subject)
            else:
                listCourse(dict,subject,course)
        elif (sys.argv[1]=="dump"):
            if (i>2):
                print
            searchCourseNum(dict,course)
        elif (sys.argv[1]=="json"):
            if (i>2):
                print
            if (course==0):
                print dict
            else:
                getJSON(dict,course)
        elif (sys.argv[1]=="info"):
            if (i>2):
                print
            printInfo(dict,course,section)
        #Disabled until I decide how to go about doing this
#        elif (sys.argv[1]=="search"):
#            print("search")
        elif (sys.argv[1]=="isOpen"):
            isOpen(dict,course,section)
        elif (sys.argv[1]=="register"):
            if (section=="0"):
                myCourse=getCourse(dict,course)
                for sections in myCourse['sections']:
                    if (sections['openStatus']):
                        register.append(sections['index'])
            else:
                if (isOpen(dict,course,section)):
                    register.append(getSectionValue(dict,course,section,"index"))
            #print(register)
            if (register!=[]):
                openWebReg(register)
         #Disabling email for now until a better solution solution can be acquired
#        elif (sys.argv[1]=="email"):
#            email=getEmail(dict,course,section)
        else:
            help()
            exit(2)
    except:
        #Blanket Try/Catch
        #Some exception was thrown, most likely from an undefined variable (i.e. section)
        #print(sys.exc_info())
        traceback.print_exc()
        retval=3
    oldSubject=subject
    i+=1
exit(retval)
