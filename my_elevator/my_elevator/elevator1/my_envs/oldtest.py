from testenv1 import Elevator
from goto import with_goto
import random
from random import randint
from numpy import *

def oldlift(floors,lift1):   #电梯控制函数，在该函数中，仅能修改电梯的state和留待状态
    zeroflag=0
    act=0
    for count in floors:
        if count.want!=0:
            zeroflag=1
    if zeroflag==0 and lift1.people==0 and lift1.waittime==0 and lift1.runtime==0:
        act=0
        lift1.state=0
    if lift1.state==1:
        if lift1.floor==24:
            act=0
            lift1.state=0
        else:
            zeroflag1=0
            for i in range(lift1.floor+1,25,1):
                if floors[i-1].want!=0:
                    zeroflag1=1
            if zeroflag1==0:
                act=0
                lift1.state=0
    if lift1.state==2:
        if lift1.floor==1:
            act=0
            lift1.state=0
        else:
            zeroflag2=0
            for i in range(1,lift1.floor,1):
                if floors[i-1].want!=0:
                    zeroflag2=1
            if zeroflag2==0:
                act=0
                lift1.state=0
    if lift1.state==0:
        if floors[lift1.floor-1].want!=0:
            if floors[lift1.floor-1].want==1 or floors[lift1.floor-1].want==3:
                act=3
            elif floors[lift1.floor-1].want==2 or floors[lift1.floor-1].want==4:
                act=4
        else:
            for count in floors:
                if count.want != 0 and (count.heigh - lift1.floor > 0):
                    act=1
                elif count.want != 0 and (count.heigh - lift1.floor < 0):
                    act=2
    if lift1.state!=0:
        if floors[lift1.floor-1].want!=lift1.state and lift1.goto[lift1.floor-1]!=1:
            if lift1.state==1:
               act=1
            elif lift1.state==2:
               act=2
        elif lift1.state==floors[lift1.floor-1].want or lift1.state==(floors[lift1.floor-1].want-2):
            if lift1.state==1:
               act=3
            elif lift1.state==2:
               act=4
        elif lift1.goto[lift1.floor-1]==1:
            if lift1.state == 1:
                act = 3
            elif lift1.state == 2:
                act = 4
    return act

env=Elevator()
while env.t<=3600 and env.done==False:
    action = oldlift(env.floors, env.lift1)
    env.step(action)
print("平均总耗时为%d，平均等待用时为%d，电梯运输速率为%d公斤每秒"%(mean(env.cost),mean(env.wait),sum(env.transweight)/env.t))