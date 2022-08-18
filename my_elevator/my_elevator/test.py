# 模型预测————————
from stable_baselines3 import DQN
import gym
from matplotlib import pyplot as plt

env_name = "elevator1:elevator-v1"
env = gym.make(env_name)
log_dir = './TrainModel/'

# model = DQN.load(log_dir + "rl_model_30000_steps",  print_system_info=True, env=env, tensorboard_log='./tensorboard')
model = DQN.load(log_dir + "rl_model_300000_steps",  print_system_info=True, env=env)

step = 0
score = []
step_time = []
state = env.reset()
while True:
    action, _ = model.predict(observation=state, deterministic=True)
    state, reward, done, info = env.step(action)
    step += 1
    score.append(reward)
    step_time.append(step)
    #env.render()
    if done:
        fig = plt.figure(1)
        plt.plot(step_time, score, color='blue', linewidth=3)
        plt.title('step_time - reward')
        plt.xlabel('step')
        plt.ylabel('reward')
        plt.show()

        state = env.reset()
        break