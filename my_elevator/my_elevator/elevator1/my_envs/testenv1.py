
import gym
from gym import spaces
from stable_baselines3.common.vec_env.dummy_vec_env import DummyVecEnv
from stable_baselines3.common.evaluation import evaluate_policy
import numpy as np
import torch as th
import time
import random
import pygame
#————————————————————————————elevator1:elevator-v1————————————————————————————————
class Elevator(gym.Env):
        def __init__(self):
            self.action_space = spaces.Discrete(5)
            obs = []
            obs.append(30)
            for i in range(1, 25, 1):
                obs.append(2)
            obs.append(3)
            obs.append(4)
            for i in range(1, 25, 1):
                obs.append(3)
                obs.append(5)
                obs.append(5)
                obs.append(5)
            self.observation_space = spaces.MultiDiscrete(obs)
            self.cost = []  # 该列表用来保存每个人乘电梯到达目的楼层的总用时时间，因在实际过程中不可能测量得到每个人的用时，所以该数据仅用作参考
            self.wait = []  # 该列表用来保存楼层按钮从按下到被响应的所需时间，强化学习会感知这部分时间，尽量使其最小
            self.transweight = []  # 运输质量，电梯质量变化的总量
            self.t = 0  # 设置程序开始时的时间，在本系统中，时间是一个离散化的值，电梯在运行中上下一层楼需要三个时间单位，暂停以接收住户需要10个时间单位。
            self.addspeed = 0.15  # 表示一楼一个时间单位生成一个乘客的概率
            # 更新显示
            self.floors = []
            self.men = []
            self.meancost=[]
            self.meanwait=[]
            self.mean_total_transweight=[]
            self.totalstep=0
            self.gotolist = []  # 生成电梯按钮列表，该列表包含24个值，按顺序代表电梯内24个楼层的按钮状态，0表示未按下，1表示按下。
            for i in range(1, 25, 1):
                self.gotolist.append(0)
            self.lift1 = Elevator.lift(1, 0, 0, 0, 0, self.gotolist, 0,0)  # 生成初始电梯，生成在一楼，最开始既不留待也不运行，处于待机状态。
            for i in range(1, 25, 1):
                self.floors.append(1)
                self.floors[i - 1] = Elevator.floor(i, 0, 0, 0, 0, 0, 0,0,0)  # 循环生成楼层对象
            self.reward = 0
            self.done = False
            self.birthlist=[]
        class person(pygame.sprite.Sprite):
            def __init__(self0, goal, loca, t, islift, end, weight):
                # 调父类来初始化子类
                pygame.sprite.Sprite.__init__(self0)
                self0.goal = goal
                self0.loca = loca
                self0.t = t
                self0.islift = islift  # 表示是否在电梯上，0表示不在电梯上，1表示在电梯上
                self0.end = end  # 表示该人的结算状态，为1表示已经结算完成
                self0.weight = weight  # 表示人的体重，该仿真系统设置其在50KG-100kg之间随机分布

        class lift(pygame.sprite.Sprite):
            def __init__(self1, floor, people, state, waittime, runtime, goto, totalweight,weightlevel):
                # 调父类来初始化子类
                pygame.sprite.Sprite.__init__(self1)
                self1.floor = floor
                self1.people = people
                self1.state = state  # state为0表示电梯待机，为1表示电梯正在向上行驶，为2表示电梯正在向下行驶
                self1.waittime = waittime  # 电梯留待计数，一旦不为0，表示开始留待，到11留待结束，表示留待需要10个时间单位
                self1.runtime = runtime  # 电梯运行计数，一旦不为0，表示电梯开始运行，到4结算一次，表示电梯在运行中每移动一个楼层需要3个时间单位
                self1.goto = goto  # 电梯内部按钮，该值为0表示内部按钮无按下
                self1.totalweight = totalweight  # 电梯内部电子秤示数
                self1.weightlevel=weightlevel  #电梯载重等级，小于500公斤为等级1，500-900公斤为等级2,900-1000公斤为等级3

        class floor(pygame.sprite.Sprite):
            def __init__(self, heigh, man, want, upwanttime, upman, downman, downwanttime,upwanttimelevel,downwanttimelevel):
                # 调父类来初始化子类
                pygame.sprite.Sprite.__init__(self)
                self.heigh = heigh
                self.man = man  # 该属性表示该层等候电梯的人数等级，0表示没人，1表示稀疏，2表示拥挤
                self.want = want  # 该属性表示该楼层的按钮状态，want为0表示无人按按钮，want为1表示向上的按钮被按下，want为2表示向下的按钮被按下，为3表示都被按下但上的优先级更高，4表示都按下，但是下的优先级更高
                self.upwanttime = upwanttime  # 该属性表示向上楼层按钮从按下为止，到现在所等待的时间
                self.upman = upman  # 该属性表示电梯中等待向上的人数
                self.downman = downman  # 该属性表示电梯中等待向下的人数
                self.downwanttime = downwanttime  # 该属性表示向下楼层按钮从按下为止，到现在所等待的时间
                self.upwanttimelevel=upwanttimelevel
                self.downwanttimelevel=downwanttimelevel
                if man == 0:
                    self.manlevel = 0
                elif man > 0 and man <= 5:
                    self.manlevel = 1
                elif man > 5:
                    self.manlevel = 2

        def checklift(self):  # 检查电梯状态,更新计数器，释放并收纳住户
            if self.lift1.totalweight==0:
                self.lift1.weightlevel=0
            elif self.lift1.totalweight<=500 and self.lift1.totalweight>0:
                self.lift1.weightlevel=1
            elif self.lift1.totalweight>500 and self.lift1.totalweight<=900:
                self.lift1.weightlevel=2
            elif self.lift1.totalweight>900:
                self.lift1.weightlevel=3
            if self.lift1.runtime != 0:
                self.lift1.runtime += 1
            if self.lift1.waittime != 0:
                self.lift1.waittime += 1
            if self.lift1.waittime == 11:  # 检查电梯，重置电梯计数器
                self.lift1.waittime = 0
                self.lift1.runtime = 1
            if self.lift1.runtime == 4:
                self.lift1.runtime = 0
                if self.lift1.state == 1:
                    self.lift1.floor += 1
                    print("电梯已经到%d层，梯内有%d人" % (self.lift1.floor, self.lift1.people))
                elif self.lift1.state == 2:
                    self.lift1.floor -= 1
                    print("电梯已经到%d层,梯内有%d人" % (self.lift1.floor, self.lift1.people))
            if self.lift1.waittime != 0:  # 电梯留待检查,在该检查中电梯开始收人或者放人
                for count in self.men:
                    if count.end == 0 and count.islift == 1 and count.goal == self.lift1.floor:
                        count.islift = 0
                        count.end = 1
                        self.lift1.people -= 1
                        self.cost.append(self.t - count.t)
                        self.lift1.totalweight -= count.weight
                        self.lift1.goto[self.lift1.floor - 1] = 0
                        self.transweight.append(count.weight)
                        self.reward += 100
                        print("有人下梯啦！")
                    elif count.end == 0 and count.islift == 0 and count.loca == self.lift1.floor \
                            and (self.floors[self.lift1.floor - 1].want == self.lift1.state or self.floors[self.lift1.floor - 1].want > 2) \
                            and ((self.lift1.totalweight + count.weight) <= 1000):
                        if (count.goal - count.loca > 0 and self.lift1.state == 1) or (count.goal - count.loca < 0 and self.lift1.state == 2):
                            count.islift = 1
                            self.lift1.people += 1
                            self.lift1.goto[count.goal - 1] = 1
                            self.floors[self.lift1.floor - 1].man -= 1
                            if count.goal > count.loca:
                                self.floors[self.lift1.floor - 1].upman -= 1
                            elif count.goal < count.loca:
                                self.floors[self.lift1.floor - 1].downman -= 1
                            self.lift1.totalweight += count.weight
                            self.reward += 100
                            print("%d层现在有%d人" % (self.lift1.floor, self.floors[self.lift1.floor - 1].man))
                            print("梯内现在有载重%d公斤"%(self.lift1.totalweight))

        def checkfloor(self):
            for count in self.floors:
                if count.man==0:
                    count.manlevel=0
                elif count.man<=5 and count.man>0:
                    count.manlevel=1
                elif count.man>5:
                    count.manlevel=2
                if count.want == 1:
                    count.upwanttime += 1
                    self.reward -= 1*count.manlevel*count.upwanttimelevel
                elif count.want == 2:
                    count.downwanttime += 1
                    self.reward -= 1*count.manlevel*count.downwanttimelevel
                elif count.want > 2:
                    count.upwanttime += 1
                    count.downwanttime += 1
                    self.reward -= (1*count.manlevel*count.downwanttimelevel+1*count.manlevel*count.upwanttimelevel)
                if count.upwanttime==0:
                    count.upwanttimelevel=0
                elif count.upwanttime<=60 and count.upwanttime>0:
                    count.upwanttimelevel=1
                elif count.upwanttime<=180 and count.upwanttime>60:
                    count.upwanttimelevel=2
                elif count.upwanttime<=300 and count.upwanttime>180:
                    count.upwanttimelevel=3
                elif count.upwanttime>300:
                    count.upwanttimelevel=4
                if count.downwanttime==0:
                    count.downwanttimelevel=0
                elif count.downwanttime<=60 and count.downwanttime>0:
                    count.downwanttimelevel=1
                elif count.downwanttime<=180 and count.downwanttime>60:
                    count.downwanttimelevel=2
                elif count.downwanttime<=300 and count.downwanttime>180:
                    count.downwanttimelevel=3
                elif count.downwanttime>300:
                    count.downwanttimelevel=4

        def step(self, act):
            self.reward = 0
            if act == 0:
                self.lift1.state = 0
                self.time_simulator(1)
            elif act == 1:
                self.lift1.state = 1
                self.lift1.runtime = 1
                self.time_simulator(3)
            elif act == 2:
                self.lift1.state = 2
                self.lift1.runtime = 1
                self.time_simulator(3)
            elif act == 3:
                self.lift1.state = 1
                self.lift1.waittime = 1
                self.time_simulator(13)
            elif act == 4:
                self.lift1.state = 2
                self.lift1.waittime = 1
                self.time_simulator(13)
            for i in range(0,24,1):
                if self.lift1.goto[i]!=0:
                    self.reward+=(80*self.lift1.weightlevel-2*abs(i-self.lift1.floor+1))
            s = []
            s.append(self.lift1.floor)
            s.extend(self.lift1.goto)
            s.append(self.lift1.state)
            s.append(self.lift1.weightlevel)
            for count in self.floors:
                s.append(count.manlevel)
                s.append(count.want)
                s.append(count.upwanttimelevel)
                s.append(count.downwanttimelevel)
            info = {}
            if self.done:
                print("-"*16)
                print("电梯该轮回合个人到达目的地平均用时%f秒,按钮从按下到被响应平均用时%f秒，总共运输质量%f吨"%(np.mean(self.cost),np.mean(self.wait),0.001*sum(self.transweight)))
                self.totalstep+=1
                self.meancost.append(np.mean(self.cost))
                self.meanwait.append(np.mean(self.wait))
                self.mean_total_transweight.append(0.001*sum(self.transweight))
            return np.array(s), self.reward, self.done, info

        def reset(self):
            self.cost=[]
            self.wait=[]
            self.transweight=[]
            self.reward = 0
            self.t=0
            self.done = False
            self.men.clear()
            self.lift1.floor = 1
            self.lift1.people = 0
            self.lift1.runtime = 0
            self.lift1.state = 0
            self.lift1.weightlevel=0
            self.gotolist = []  # 生成电梯按钮列表，该列表包含24个值，按顺序代表电梯内24个楼层的按钮状态，0表示未按下，1表示按下。
            for i in range(1, 25, 1):
                self.gotolist.append(0)
            self.lift1.goto = self.gotolist
            self.lift1.waittime = 0
            self.lift1.totalweight = 0
            for count in self.floors:
                count.downman = 0
                count.upwanttime = 0
                count.downwanttime = 0
                count.want = 0
                count.upman = 0
                count.man = 0
                count.upwanttimelevel=0
                count.downwanttimelevel=0
            s = []
            s.append(self.lift1.floor)
            s.extend(self.lift1.goto)
            s.append(self.lift1.state)
            s.append(self.lift1.weightlevel)
            for count in self.floors:
                s.append(count.manlevel)
                s.append(count.want)
                s.append(count.upwanttimelevel)
                s.append(count.downwanttimelevel)
            return np.array(s)

        def render(self, mode='human'):
            white = (255, 255, 255)
            yellow = (255, 255, 102)
            black = (0, 0, 0)
            red = (213, 50, 80)
            green = (0, 255, 0)
            blue = (50, 153, 213)
            screenx = 1200
            screeny = 768
            pygame.init()
            screen = pygame.display.set_mode((screenx, screeny))
            pygame.display.set_caption('Hitdog')
            f = pygame.font.Font('C:/Windows/Fonts/simhei.ttf', 20)
            close_lift_surface = pygame.image.load("close_lift.png").convert()
            open_lift_surface = pygame.image.load("open_lift.png").convert()
            want0_surface = pygame.image.load("want0.png").convert()
            want1_surface = pygame.image.load("want_1.png").convert()
            want2_surface = pygame.image.load("want_2 .png").convert()
            want34_surface = pygame.image.load("want_34.png").convert()
            remind0_surface = pygame.image.load("remind0.png").convert()
            remind1_surface = pygame.image.load("remind1.png").convert()
            interval = screeny / 24
            clock = pygame.time.Clock()
            for i in range(0, 24, 1):
                pygame.draw.line(screen, blue, [0, screeny - i * interval], [screenx, screeny - i * interval], 1)
                text = f.render("%d"%(self.floors[i].man), True, green, None)
                textRect = text.get_rect()
                textRect.center = ((screenx/2)-15, screeny-(i+1)*interval+10)
                screen.blit(text, textRect)
                if self.floors[i].want==0:
                    screen.blit(want0_surface,(screenx/2+40,screeny-(i+1)*interval))
                elif self.floors[i].want==1:
                    screen.blit(want1_surface, (screenx / 2 + 40, screeny - (i + 1) * interval))
                elif self.floors[i].want==2:
                    screen.blit(want2_surface, (screenx / 2 + 40, screeny - (i + 1) * interval))
                elif self.floors[i].want>2:
                    screen.blit(want34_surface, (screenx / 2 + 40, screeny - (i + 1) * interval))
                if self.lift1.waittime!=0 and self.lift1.floor==(i+1):
                    screen.blit(open_lift_surface, (screenx / 2, screeny - (i + 1) * interval))
                else :
                    screen.blit(close_lift_surface, (screenx / 2, screeny - (i + 1) * interval))
                if (i + 1) != self.lift1.floor:
                    screen.blit(remind0_surface, ((screenx / 2)+5 , screeny - (i + 1) * interval))
                else:
                    screen.blit(remind1_surface, ((screenx / 2) +5, screeny - (i + 1) * interval))
            lifttext = f.render("%d" % (self.lift1.people), True, red, None)
            lifttextRect = lifttext.get_rect()
            lifttextRect.center = (screenx / 2 + 10, screeny - self.lift1.floor * interval+10)
            screen.blit(lifttext, lifttextRect)
            pygame.display.flip()
            clock.tick(15)
            for event in pygame.event.get():
                # 判断用户是否点了"X"关闭按钮,并执行if代码段
                if event.type == pygame.QUIT:
                    # 卸载所有模块
                    pygame.quit()
                    # 终止程序，确保退出程序
                    # sys.exit()
        def seed(self, seed=None):
            pass
        def addman(self,birthplace,goal):
            self.floors[birthplace-1].man+=1
            if goal > birthplace:
                self.floors[birthplace - 1].upman += 1
                if self.floors[birthplace - 1].want == 0:
                    self.floors[birthplace - 1].want = 1
                elif self.floors[birthplace - 1].want == 2:
                    self.floors[birthplace - 1].want = 4
            elif goal < birthplace:
                self.floors[birthplace - 1].downman += 1
                if self.floors[birthplace - 1].want == 0:
                    self.floors[birthplace - 1].want = 2
                elif self.floors[birthplace - 1].want == 1:
                    self.floors[birthplace - 1].want = 3
        def time_simulator(self, time):
            for i in range(1, time + 1):
                self.t += 1
                p = random.random()
                if p > (1 - self.addspeed):
                    x = random.randint(-21, 24)
                    y1 = random.randint(2, 24)
                    y2 = random.randint(-21, 24)
                    w = random.randint(0, 50)
                    if x <= 1 and self.floors[1 - 1].man <= 20:
                        self.men.append(Elevator.person(y1, 1, self.t, 0, 0, 50 + w))
                        self.birthlist.append([self.t,1,y1])
                        self.floors[1 - 1].man += 1
                        if y1 > 1:
                            self.floors[1 - 1].upman += 1
                            if self.floors[1 - 1].want == 0:
                                self.floors[1 - 1].want = 1
                            elif self.floors[1 - 1].want == 2:
                                self.floors[1 - 1].want = 4
                        elif y1 < 1:
                            self.floors[1 - 1].downman += 1
                            if self.floors[1 - 1].want == 0:
                                self.floors[1 - 1].want = 2
                            elif self.floors[1 - 1].want == 1:
                                self.floors[1 - 1].want = 3
                    elif x > 1 and (y2 <= 1 or y2 == x) and self.floors[x - 1].man <= 20:
                        self.men.append(Elevator.person(1, x, self.t, 0, 0, 50 + w))
                        self.birthlist.append([self.t,x,1])
                        self.floors[x - 1].man += 1
                        if 1 > x:
                            self.floors[x - 1].upman += 1
                            if self.floors[x - 1].want == 0:
                                self.floors[x - 1].want = 1
                            elif self.floors[x - 1].want == 2:
                                self.floors[x - 1].want = 4
                        elif 1 < x:
                            self.floors[x - 1].downman += 1
                            if self.floors[x - 1].want == 0:
                                self.floors[x - 1].want = 2
                            elif self.floors[x - 1].want == 1:
                                self.floors[x - 1].want = 3
                    elif x > 1 and (y2 > 1 and y2 != x) and self.floors[x - 1].man <= 20:
                        self.men.append(Elevator.person(y2, x, self.t, 0, 0, 50 + w ))
                        self.birthlist.append([self.t,x,y2])
                        self.floors[x - 1].man += 1
                        if y2 > x:
                            self.floors[x - 1].upman += 1
                            if self.floors[x - 1].want == 0:
                                self.floors[x - 1].want = 1
                            elif self.floors[x - 1].want == 2:
                                self.floors[x - 1].want = 4
                        elif y2 < x:
                            self.floors[x - 1].downman += 1
                            if self.floors[x - 1].want == 0:
                                self.floors[x - 1].want = 2
                            elif self.floors[x - 1].want == 1:
                                self.floors[x - 1].want = 3
                Elevator.checklift(self)
                Elevator.checkfloor(self)
                #Elevator.render(self)
                if self.lift1.floor > 24 or self.lift1.floor <= 0:
                    self.reward -= 10000
                    self.done = True
                if self.t == 3600:
                    self.done = True
                for count in self.floors:  # 遍历所有楼层，无人楼层的按钮被赋0
                    if count.upman == 0:
                        if count.want == 1:
                            count.want = 0
                            self.wait.append(count.upwanttime)  # 等待时间被列表储存
                            count.upwanttime = 0
                        elif count.want > 2:
                            count.want = 2
                            self.wait.append(count.upwanttime)
                            count.upwanttime = 0
                    if count.downman == 0:
                        if count.want == 2:
                            count.want = 0
                            self.wait.append(count.downwanttime)
                            count.downwanttime = 0
                        elif count.want > 2:
                            count.want = 1
                            self.wait.append(count.downwanttime)
                            count.downwanttime = 0