from gym.envs.registration import register

register(
    id='ransim-v0',
    entry_point='gym_ransim.envs:RanSimEnv',
)