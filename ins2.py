import numpy as np
import pandas as pd
import re
import string
import pulp
import  xml.dom.minidom
from xml.etree import ElementTree as ET

per=ET.parse('D:\download\山下 先生\instances1_24solutions\\Instance2.ros')

dom = xml.dom.minidom.parse('D:\download\山下 先生\instances1_24solutions\\Instance2.ros')
root = dom.documentElement

count1=0
p1=per.findall('Employees/Employee')
for oneper in p1:
    count1=count1+1
    print(oneper.tag)
EmpNum=count1

count2=0
p2=per.findall('ShiftTypes/Shift')
for oneper in p2:
    count2=count2+1
    print(oneper.tag)
ShiftType=count2

duration=np.zeros(ShiftType)
dd=dom.getElementsByTagName('Duration')
for m in range(ShiftType):
    duration[m]=int(dd[m].firstChild.data ) 
print(duration)

bimax=np.zeros(EmpNum)
bimin=np.zeros(EmpNum)
amax=np.zeros(EmpNum)

cimax=np.zeros(EmpNum)
cimin=np.zeros(EmpNum)
oimin=np.zeros(EmpNum)

for m in range(EmpNum):
    t=0
    p2=root.getElementsByTagName('Contract')
    for oneper in p2:
        if(len(oneper.getAttribute("ID"))==1):
            t=ord(oneper.getAttribute("ID"))
            itemlist = oneper.getElementsByTagName('MaxSeq')
            item1 = itemlist[0]
            cimax[t-65]= int(item1.getAttribute("value"))
            
            itemlist = oneper.getElementsByTagName('MinSeq')
            for it in itemlist:
            #item2 = itemlist[0]
            #item3 = itemlist[1]
            #cimin[t-65]= int(item2.getAttribute("value"))
            #oimin[t-65]= int(item3.getAttribute("value"))
                if (it.getAttribute("shift")=="$"):
                    cimin[t-65]= int(it.getAttribute("value"))
                elif(it.getAttribute("shift")=="-"):
                    oimin[t-65]= int(it.getAttribute("value"))
                
            itemlist = oneper.getElementsByTagName('Count')
            c1=itemlist[0]
            c2=itemlist[1]
            c3=itemlist[2]
            bimax[t-65]=int(c1.firstChild.data)
            bimin[t-65]=int(c2.firstChild.data)
            amax[t-65]=int(c3.firstChild.data)
print(cimax,cimin,oimin,bimax,bimin,amax)

rr=dom.getElementsByTagName('MinRestTime')
r1=rr[0]
minRestTime=r1.firstChild.data  
print(minRestTime)

DayNum=14 
prob = pulp.LpProblem('benchmark', pulp.LpMinimize) # minimize
xidt = pulp.LpVariable.dicts("Xidt",(range(EmpNum), range(DayNum), range(ShiftType+1)),0,1,pulp.LpInteger)
#array p and q are penalty arrays
pen= np.zeros((EmpNum,DayNum,ShiftType))
q= np.zeros((EmpNum,DayNum,ShiftType))

weenk_num=2
k= pulp.LpVariable.dicts("K",(range(EmpNum),range(weenk_num)),0,1,pulp.LpInteger)

#constraints

#valid shift constraints
for j in range(DayNum):
    prob += xidt[3][j][2]==0
    prob += xidt[4][j][1]==0
    prob += xidt[10][j][1]==0
    prob += xidt[11][j][1]==0

for i in range (EmpNum):

    #shift off or shift on
    for j in range (DayNum):
        prob += xidt[i][j][0]+xidt[i][j][1]+xidt[i][j][2] == 1
        
    #duration constraints
    prob += pulp.lpSum([xidt[i][j][m+1]*duration[m] for j in range(DayNum) for m in range(ShiftType)]) <= bimax[i]
    prob += pulp.lpSum([xidt[i][j][m+1]*duration[m] for j in range(DayNum) for m in range(ShiftType)]) >= bimin[i]
    
    #weekend constraints
    prob += pulp.lpSum([k[i][m] for m in range (weenk_num)])<= amax[i]
    for m in range (weenk_num):
        prob += pulp.lpSum([xidt[i][7*m+5][s+1] for s in range(ShiftType)])+ pulp.lpSum([xidt[i][7*m+6][s+1] for s in range(ShiftType)])>=k[i][m]
        prob += pulp.lpSum([xidt[i][7*m+5][s+1] for s in range(ShiftType)])+ pulp.lpSum([xidt[i][7*m+6][s+1] for s in range(ShiftType)])<=2*k[i][m]
        
    #consecutive shift on or shift off constraints
    for j in range(DayNum-int(cimax[i])):
        prob += pulp.lpSum([xidt[i][j+v][t+1] for v in range(int(cimax[i])+1) for t in range(ShiftType)])<= cimax[i]
    
    if (cimin[i]>0):
        for s in range (1,int(cimin[i])):
            for d in range(1,DayNum-(s+1)+1):
                prob += pulp.lpSum([xidt[i][d-1][t+1] for t in range(ShiftType)]) + s -pulp.lpSum([xidt[i][j-1][t+1] for j in range(d+1,d+s+1) for t in range(ShiftType)]) + pulp.lpSum([xidt[i][d+s][t+1] for t in range(ShiftType)]) >= 1
    
    for s in range (1,int(oimin[i])):
        for d in range(1,DayNum-(s+1)+1):
            prob += xidt[i][d-1][0] + s -pulp.lpSum([xidt[i][j-1][0] for j in range(d+1,d+s+1)]) + xidt[i][d+s+1-1][0] >= 1
    
    #minRestTime constraints
    for j in range (DayNum-1):
        prob += xidt[i][j][2]+xidt[i][j+1][1]<=1

#fixed sssignment constraints
FixedAssignment=[]
p3=per.findall('FixedAssignments/Employee/EmployeeID')
for oneper in p3:
    FixedAssignment.append(ord(oneper.text))
print(FixedAssignment)

day1=[]
p4=per.findall('FixedAssignments/Employee/Assign/Day')
for oneper in p4:
    day1.append(int(oneper.text))
print(day1)

for i in range (EmpNum): 
    prob += xidt[FixedAssignment[i]-65][day1[i]][0]==1



#objective

#Shift off penalty
count3=0
ShiftOffRequests=[]
p5=per.findall('ShiftOffRequests/ShiftOff/EmployeeID')
for oneper in p5:
    count3=count3+1
    ShiftOffRequests.append(ord(oneper.text))
print(ShiftOffRequests)

day2=[]
p6=per.findall('ShiftOffRequests/ShiftOff/Day')
for oneper in p6:
    day2.append(int(oneper.text))
print(day2)

w1=[]
itemlist1 = root.getElementsByTagName('ShiftOff')
for m in range(count3):
    w1.append(int(itemlist1[m].getAttribute("weight")))
print (w1)

shift1=[]
p7=per.findall('ShiftOffRequests/ShiftOff/Shift')
for oneper in p7:
    if (oneper.text=="E"):
        shift1.append(0)
    elif(oneper.text=="L"):
        shift1.append(1)
print(shift1)

for m in range(count3):
    pen[ShiftOffRequests[m]-65][day2[m]][shift1[m]]=w1[m]
    
#Shift on penalty
count4=0
ShiftOnRequests=[]
p8=per.findall('ShiftOnRequests/ShiftOn/EmployeeID')
for oneper in p8:
    count4=count4+1
    ShiftOnRequests.append(ord(oneper.text))
print(ShiftOnRequests)

day3=[]
p9=per.findall('ShiftOnRequests/ShiftOn/Day')
for oneper in p9:
    day3.append(int(oneper.text))
print(day3)

w2=[]
itemlist2 = root.getElementsByTagName('ShiftOn')
for m in range(count4):
    w2.append(int(itemlist2[m].getAttribute("weight")))
print (w2)

shift2=[]
p10=per.findall('ShiftOnRequests/ShiftOn/Shift')
for oneper in p10:
    if (oneper.text=="E"):
        shift2.append(0)
    elif(oneper.text=="L"):
        shift2.append(1)
print(shift2)

for m in range(count4):
    q[ShiftOnRequests[m]-65][day3[m]][shift2[m]]=w2[m]
    
#Employee Nmuber penalty
cover=[]
w3=[]
w4=[]

cover1=[]
cover2=[]
wmin1=[]
wmin2=[]
wmax1=[]
wmax2=[]
p=root.getElementsByTagName('DateSpecificCover')
for oneper in p:
    itemlist = oneper.getElementsByTagName('Min')
    c1=itemlist[0]
    c2=itemlist[1]
    cover1.append(int(c1.firstChild.data))
    cover2.append(int(c2.firstChild.data))
    wmin1.append(int(c1.getAttribute("weight")))
    wmin2.append(int(c2.getAttribute("weight")))
    itemlist1 = oneper.getElementsByTagName('Max')
    d1=itemlist1[0]
    d2=itemlist1[1]
    wmax1.append(int(d1.getAttribute("weight")))
    wmax2.append(int(d2.getAttribute("weight")))
print(cover1,cover2,wmin1,wmin2,wmax1,wmax2)

cover.append(cover1)
cover.append(cover2)
w3.append(wmin1)
w3.append(wmin2)
w4.append(wmax1)
w4.append(wmax2)

y = pulp.LpVariable.dicts("Y",(range(DayNum),range(ShiftType)),lowBound=0)
z = pulp.LpVariable.dicts("Z",(range(DayNum),range(ShiftType)),lowBound=0)
for j in range(DayNum):
    for s in range(ShiftType):
        prob+=pulp.lpSum([xidt[i][j][s+1] for i in range(EmpNum)])-z[j][s]+y[j][s]==cover[s][j]
        
prob += pulp.lpSum([y[j][s]*w3[s][j] for j in range(DayNum)] for s in range(ShiftType))+ pulp.lpSum([z[j][s]*w4[s][j] for j in range(DayNum) for s in range(ShiftType)]) + pulp.lpSum([(1-xidt[i][j][s+1])*q[i][j][s]for i in range(EmpNum) for j in range (DayNum) for s in range(ShiftType)])+pulp.lpSum([xidt[i][j][s+1]*pen[i][j][s] for i in range(EmpNum) for j in range (DayNum) for s in range(ShiftType)])
s = prob.solve()
print (pulp.LpStatus[s])

#print result
for v in prob.variables():
    print(v.name, "=", v.varValue)
print("******************************************************************************************************************************************************************")
print(prob.objective.value())

for i in range(EmpNum):
    for j in range (DayNum):
        for s in range(ShiftType+1):
            print(xidt[i][j][s].value(), end=" ")
        print(end="     ")
    print()
print("*****************************************************************************************************************************************************************")

for s in range(ShiftType):
    for j in range(DayNum):
        print(y[j][s].value(), end=" ")
    print()
