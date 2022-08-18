from gym.envs.registration import register
register(
    id='elevator-v1',
    entry_point='elevator1.my_envs.testenv1:Elevator',
)