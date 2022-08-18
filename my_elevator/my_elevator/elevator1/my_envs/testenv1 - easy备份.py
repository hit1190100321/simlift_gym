
import gym
from gym import spaces
from stable_baselines3.common.vec_env.dummy_vec_env import DummyVecEnv
from stable_baselines3.common.evaluation import evaluate_policy
import numpy as np
import torch as th
import time
import random

#————————————————————————————elevator1:elevator-v1————————————————————————————————
class Elevator(gym.Env):
    def __init__(self):
        self.action_space = spaces.Discrete(3)
        #observation_high = np.array([
        #    np.finfo(np.float32).max,
        #    np.finfo(np.float32).max])
        #self.observation_space = spaces.Box(-observation_high,observation_high)
        self.observation_space = spaces.MultiDiscrete([15,50])
        self.floor = 1
        self.reward = 0
        self.t = 0
        self.done = False

    def step(self, action):
        #self.reward -= 1
        self.reward=0
        self.t += 1
        if action == 0:
            pass
        elif action == 1:
            self.floor += 1
        elif action == 2:
            self.floor -= 1
        if self.floor <= 0 or self.floor > 10:
            self.reward -= 100
            self.done=True
        if self.t < 10:
            self.reward += (10-abs(self.floor-4))
        elif self.t>=15 and self.t<20:
            self.reward += (10 - abs(self.floor - 6))
        elif self.floor == 6 and self.t == 20:
            self.reward += 100
            self.done = True
            print("完成任务！")
        if self.t>=30:
            self.done=True
        print("已经到达%d层,此时时间为%d" % (self.floor,self.t))
        state = [self.floor, self.t]
        state = np.array(state)
        info = {}
        if self.done:
            print("-"*16)
        return state, self.reward, self.done, info

    def reset(self):
        self.floor = 1
        self.t = 0
        self.reward = 0
        self.done = False
        #state=[self.floor,self.t]
        state = np.array([self.floor, self.t])
        return state

    def render(self, mode='human'):
        pass

    def seed(self, seed=None):
        pass
