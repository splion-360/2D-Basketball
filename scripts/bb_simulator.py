from environment import BasketBallEnv
from ray.rllib.env.multi_agent_env import MultiAgentEnv

policy_mapping_dict = {
    "all_scenario": {
        "description": "bb all scenarios",
        "team_prefix": ("player_1","player_2"),
        "all_agents_one_policy": False,
        "one_agent_one_policy": True,
    },
}


class BBEnvWrapper(MultiAgentEnv):
    def __init__(self,env_config):
        if len(env_config) == 0:
            env_config= {
                            "grid": False,
                            "map_name": "Simple BB",
                            "n_players": 4,
                            "n_teams": 2,
                            "ticks": 50,
                            "with_pygame": False
                        }
        n_players = env_config['n_players']
        n_teams =  env_config['n_teams']
        grid =  env_config['grid']
        ticks = env_config['ticks']
        with_pygame = env_config['with_pygame']
        agent_params = {'shooting_ability': (0.9,0.9,0.3,0.3),'stepSize':(40,40,40,40),'defense_ability':(0.3,0.3,0.7,0.7),'pass_ability':(0.9,0.9,0.6,0.6)}

        map = env_config['map_name']
        
        self.env = BasketBallEnv(n_players,n_teams,agent_params,grid,ticks,with_pygame)
        self.action_space = self.env.action_space(None)
        self.observation_space = self.env.observation_space(None)
        self.agents = self.env.agents
        
    def reset(self):
        obs = self.env.reset()
        return obs
    
    def step(self, action:dict):
        obs, rew, terminated, truncated, info = self.env.step(action)

        
        dones = {'__all__':any(list(terminated.values())+list(truncated.values()))}

        return obs, rew, dones, info
    def close(self):
        self.env.close()
    
    def get_env_info(self):
        env_info = {
            "space_obs": self.observation_space,
            "space_act": self.action_space,
            "num_agents": len(self.agents),
            "episode_limit": 400,
            "policy_mapping_info": policy_mapping_dict
        }
        return env_info
