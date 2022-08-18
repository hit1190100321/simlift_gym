import gym
from stable_baselines3.common.env_checker import check_env
from stable_baselines3 import DQN
from stable_baselines3.common.env_util import make_vec_env
from stable_baselines3.common.vec_env import SubprocVecEnv,VecNormalize,DummyVecEnv
from stable_baselines3.common.callbacks import CheckpointCallback
import matplotlib.pyplot as plt
from stable_baselines3 import PPO

env_name = "elevator1:elevator-v1"
env = gym.make(env_name)
# check_env(env)
env.reset()
# env = DummyVecEnv([lambda : env])
model = PPO("MlpPolicy",
            env=env,
            batch_size=128,
            gae_lambda=0.98,
            gamma=0.999,
            n_epochs=4,
            ent_coef=0.01,
            verbose=1,
            tensorboard_log="./tensorboard/LunarLander-v2/"
)

log_dir = './ppotrain'
checkpoint_callback = CheckpointCallback(save_freq=50000, save_path=log_dir, name_prefix='rl_model')
model.learn(total_timesteps=50000000, callback=checkpoint_callback, tb_log_name="ppofirst_run")
model.save(log_dir + "/newmodel1")