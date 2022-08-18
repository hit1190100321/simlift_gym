import gym
from stable_baselines3.common.env_checker import check_env
from stable_baselines3 import DQN
from stable_baselines3.common.env_util import make_vec_env
from stable_baselines3.common.vec_env import SubprocVecEnv,VecNormalize,DummyVecEnv
from stable_baselines3.common.callbacks import CheckpointCallback
import matplotlib.pyplot as plt



if __name__ == '__main__':
    env_name = "elevator1:elevator-v1"
    env = gym.make(env_name)
    # check_env(env)
    env.reset()
    # env = DummyVecEnv([lambda : env])

    model = DQN(
        "MlpPolicy",
        env=env,
        learning_rate=1e-5,
        batch_size=128,
        buffer_size=50000,
        learning_starts=0,
        target_update_interval=25,
        policy_kwargs={"net_arch" : [256, 256]},
        verbose=1,
        tensorboard_log='./tensorboard'
    )

    log_dir = './TrainModel'
    checkpoint_callback = CheckpointCallback(save_freq=50000, save_path=log_dir, name_prefix='rl_model')
    model.learn(total_timesteps=50000000, callback=checkpoint_callback, tb_log_name="first_run")
    model.save(log_dir + "/newmodel1")
    plt.plot(env.totalstep,env.meancost)
    plt.show()



