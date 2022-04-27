import numpy as np
import pandas as pd
import re
import string
import pulp
import  xml.dom.minidom
from xml.etree import ElementTree as ET

per=ET.parse('D:\download\山下 先生\instances1_24solutions\\Instance1.ros')

dom = xml.dom.minidom.parse('D:\download\山下 先生\instances1_24solutions\\Instance1.ros')
root = dom.documentElement

itemlist = root.getElementsByTagName('MaxSeq')
item1 = itemlist[0]
cimax= int(item1.getAttribute("value"))
itemlist = root.getElementsByTagName('MinSeq')
item2 = itemlist[0]
item3 = itemlist[1]
cimin= int(item2.getAttribute("value"))
oimin= int(item3.getAttribute("value"))
print(cimax,cimin,oimin)

cc=dom.getElementsByTagName('Count')
c1=cc[0]
c2=cc[1]
c3=cc[2]
bimax= int(c1.firstChild.data)
bimin= int(c2.firstChild.data)
amax= int(c3.firstChild.data)
print(bimax,bimin,amax)

count1=0
p1=per.findall('Employees/Employee')
for oneper in p1:
    count1=count1+1
    print(oneper.tag)
EmpNum=count1
    
dd=dom.getElementsByTagName('Duration')
d1=dd[0]
duration=int(d1.firstChild.data ) 
print(duration)

rr=dom.getElementsByTagName('MinRestTime')
r1=rr[0]
minRestTime=r1.firstChild.data  
print(minRestTime)

DayNum=14  
shifttype=2

prob = pulp.LpProblem('benchmark', pulp.LpMinimize) # minimize
xidt = pulp.LpVariable.dicts("Xidt",(range(EmpNum), range(DayNum), range(shifttype)),0,1,pulp.LpInteger)
# 1 if employee i is assigned shift type t on day d, 0 otherwise 
#penalty= pulp.LpVariable.dicts("Penalty",(range(EmpNum), range(DayNum), range(shifttype)),0,1,pulp.LpInteger)
penalty= np.zeros((EmpNum,DayNum,shifttype))

weenk_num=2
k= pulp.LpVariable.dicts("K",(range(EmpNum),range(weenk_num)),0,1,pulp.LpInteger)


#constraints
for i in range (EmpNum):

    #shift off or shift on
    for j in range (DayNum):
        prob += xidt[i][j][0]+xidt[i][j][1] == 1
    
    #duration constraints
    prob += pulp.lpSum([xidt[i][j][1]*duration for j in range(DayNum)]) <= bimax
    prob += pulp.lpSum([xidt[i][j][1]*duration for j in range(DayNum)]) >= bimin
    
    #weekend constraints
    #prob += xidt[i][5][1]+xidt[i][6][1]>= 1
    #prob += xidt[i][12][1]+xidt[i][13][1]>= 1 
    #prob += xidt[i][5][1]==xidt[i][6][1]
    #prob += xidt[i][12][1]==xidt[i][13][1]
    prob += pulp.lpSum([k[i][m] for m in range (weenk_num)])<= amax
    for m in range (weenk_num):
        prob += xidt[i][7*m+5][1]+ xidt[i][7*m+6][1]>=k[i][m]
        prob += xidt[i][7*m+5][1]+ xidt[i][7*m+6][1]<=2*k[i][m]
    
    
    #consecutive shift on or shift off constraints
    for j in range(DayNum-cimax):
        prob += pulp.lpSum([xidt[i][j+v][1] for v in range(cimax+1)])<= cimax
        # print(pulp.lpSum([xidt[i][j+v][1] for v in range(cimax)]))
        
        
    #for j in range(DayNum-cimin):
    for s in range (1,cimin-1+1):
        for d in range(1,DayNum-(s+1)+1):
            prob += xidt[i][d-1][1] + s -pulp.lpSum([xidt[i][j-1][1] for j in range(d+1,d+s+1)]) + xidt[i][d+s+1-1][1] >= 1
            # print(xidt[i][d-1][1] + s -pulp.lpSum([xidt[i][j-1][1] for j in range(d+1,d+s+1)]) + xidt[i][d+s+1-1][1])
            
    #STOP
    #for j in range(DayNum-oimin):
    for s in range (1,oimin-1+1):
        for d in range(1,DayNum-(s+1)+1):
            prob += xidt[i][d-1][0] + s -pulp.lpSum([xidt[i][j-1][0] for j in range(d+1,d+s+1)]) + xidt[i][d+s+1-1][0] >= 1

FixedAssignment=[]
p2=per.findall('FixedAssignments/Employee/EmployeeID')
for oneper in p2:
    FixedAssignment.append(ord(oneper.text))
print(FixedAssignment)

day1=[]
p3=per.findall('FixedAssignments/Employee/Assign/Day')
for oneper in p3:
    day1.append(int(oneper.text))
print(day1)

#fixed assignment constrains
print("**************************************")
for i in range (EmpNum): 
    prob += xidt[FixedAssignment[i]-65][day1[i]][1]==0  
    print(xidt[FixedAssignment[i]-65][day1[i]][0])
    print(xidt[FixedAssignment[i]-65][day1[i]][1])
print("***************************************")
#objective

#Shift off penalty

count2=0
ShiftOffRequests=[]
p4=per.findall('ShiftOffRequests/ShiftOff/EmployeeID')
for oneper in p4:
    count2=count2+1
    ShiftOffRequests.append(ord(oneper.text))
print(ShiftOffRequests)

day2=[]
p5=per.findall('ShiftOffRequests/ShiftOff/Day')
for oneper in p5:
    day2.append(int(oneper.text))
print(day2)

w1=[]
itemlist1 = root.getElementsByTagName('ShiftOff')
for m in range(count2):
    w1.append(int(itemlist1[m].getAttribute("weight")))
print (w1)

for m in range(count2):
    penalty[ShiftOffRequests[m]-65][day2[m]][1]=w1[m]
    
#Shift on penalty

count3=0
ShiftOnRequests=[]
p6=per.findall('ShiftOnRequests/ShiftOn/EmployeeID')
for oneper in p6:
    count3=count3+1
    ShiftOnRequests.append(ord(oneper.text))
print(ShiftOnRequests)

day3=[]
p7=per.findall('ShiftOnRequests/ShiftOn/Day')
for oneper in p7:
    day3.append(int(oneper.text))
print(day3)

w2=[]
itemlist2 = root.getElementsByTagName('ShiftOn')
for m in range(count3):
    w2.append(int(itemlist2[m].getAttribute("weight")))
print (w2)

for m in range(count3):
    penalty[ShiftOnRequests[m]-65][day3[m]][0]=w2[m]


#Employee Nmuber penalty
cover=[]
p8=per.findall('CoverRequirements/DateSpecificCover/Cover/Min')
for oneper in p8:
    cover.append(int(oneper.text))
print(cover)

w3=[]
w4=[]
for itemlist3 in per.findall('CoverRequirements/DateSpecificCover/Cover/Min'):
     w3.append(int(itemlist3.get('weight')))
for itemlist4 in per.findall('CoverRequirements/DateSpecificCover/Cover/Max'):
     w4.append(int(itemlist4.get('weight')))


y = pulp.LpVariable.dicts("Y",(range(DayNum)),lowBound=0)
z = pulp.LpVariable.dicts("Z",(range(DayNum)),lowBound=0)
#Num=np.zeros(DayNum)
#NumPenalty=np.zeros(DayNum)
for j in range(DayNum):
   # for i in range (EmpNum):
    #    if (xidt[i][j][1]==1):
     #       Num[j]+=1 

    #if (Num[j]>cover[j]):
    #    NumPenalty[j]= w4[j]
    #if (Num[j]<cover[j]):
    #    NumPenalty[j]= w3[j]
        
    prob+=pulp.lpSum([xidt[i][j][1] for i in range(EmpNum)])-z[j]+y[j]==cover[j]

prob += pulp.lpSum([y[j]*w3[j] for j in range(DayNum)])+ pulp.lpSum([z[j]*w4[j] for j in range(DayNum)]) + pulp.lpSum([xidt[i][j][v]*penalty[i][j][v] for i in range(EmpNum) for j in range (DayNum) for v in range(shifttype)])
s = prob.solve()
print (pulp.LpStatus[s])

# print result
for v in prob.variables():
    print(v.name, "=", v.varValue)
print(prob.objective.value())

for i in range(EmpNum):
    for j in range (DayNum):
            print(xidt[i][j][1].value(), end=" ")
    print()
print("***************************************************")
for j in range(DayNum):
    print(y[j].value(), end=" ")
#for j in range(DayNum):
#    print(z[j].value(), end=" ")
