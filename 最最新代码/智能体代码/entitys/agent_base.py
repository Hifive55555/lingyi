# _*_ coding: UTF-8 _*_

from abc import abstractmethod

from corekit.agents.base import Agent
from corekit.utils.typings import ActionExe, ObsArray
from .player import Player  # 选手常用方法文件


class RLAgentBase(Agent, Player):
    """
    强化学习智能体基类
    """
    """配置状态空间、动作空间"""
    # action_space: gym.Space = gym.spaces.MultiDiscrete([5, 2])  # 动作空间维度---需用户在智能体类中定义
    # observation_space: gym.Space = gym.spaces.Box(low=-np.inf, high=+np.inf, shape=(282,))  # 状态空间维度--需用户在智能体类中定义

    def __init__(self, agent_conf: dict = None):
        if agent_conf is None:
            agent_conf = {}
        super().__init__(agent_conf)
        side_name = ""
        if 'side' in agent_conf:
            side_name = agent_conf["side"]
        Player.__init__(self, side_name)
        self.model = None  # 智能体神经网络模型，客户端调度智能体使用时需加载模型用于决策
        # 用户需重写load_model函数，加载生成模型，训练时在智能体脚本文件同级的model目录下会存储模型文件，
        # 例如"model_best.h5"，代表训练好的最优模型文件。
        self.is_rule_agent = False
        self.agent_unit_name = agent_conf["agent_name"]  # 强化学习智能体控制的单元名称
        self.side = agent_conf['side']  # 对应强化学习智能体推演方
        self.enemy_side = agent_conf['enemy_side']  # config.py中配置的敌方，计算观测和奖励时可能有用
        self.agent_unit_id = ""  # 强化学习控制的智能体单元的guid
        self.agent_file_path = ""  # 智能体脚本路径

    @abstractmethod
    def step(self, time_elapse, situation):
        """
        客户端导入此强化学习智能体后，按推演时间决策间隔（self.agent_decision_time，可赋值修改）会自动调用一次此函数；
        可自动计算当前态势的每个智能体（客户端中智能体脚本的输入单元，每个单元一个智能体）观测空间（用户编写的obs_trans函数），
        通过加载的模型，输入计算的观测，输出动作数据；
        传入模型输出的动作数据，再调用act_trans函数，
        生成推演系统动作指令信息（即action_dict）, 最后调用step_rl函数对推演系统指令调用；
        obs_trans函数、act_trans函数和step_rl函数都是训练智能体时会被调用的函数，客户端应用智能体时可再次被使用；
        实现示例参考agent/rl_gent/fighter/Fighter.py
        以下是标准实现代码。
        :param time_elapse:int, 推演仿真时间，单位：秒，取值0-推演总时间秒数
        :param situation: tuple, 单元字典和探测到的目标字典, units dict, contacts dict
        :return: None
        """
        # 这里可叠加其他规则类代码，实现规则和强化学习结合的决策。
        all_agents_actions = {}
        select_units_guid = self.client_info['unit'].keys()  # 客户端选择的单元对象id
        units = situation[0]
        for guid in select_units_guid:
            # 遍历客户端配置的单元guid
            if guid in units:
                # 单元guid在收到的态势中
                self.agent_unit_id = guid
                unit_obs = self.obs_trans(situation)  # 动作转换
                tensorout = self.get_model_out(unit_obs)  # 模型前向输出
                action = self.action(tensorout)  # 生成动作数据
                agent_action_dict = self.act_trans(action, situation)  # 动作数据转换为指令信息
                all_agents_actions[guid] = agent_action_dict
        self.step_rl(time_elapse, situation, all_agents_actions)  # 指令下达

    def action(self, out):
        """
        将神经网络的输出out, 转变成行动策略 action.
        配置多单元的多智能体强化学习算法中，每个单元算一个智能体，每步决策调用一次每个智能体此函数。
        实现示例参考agent/rl_gent/fighter/Fighter.py
        :param out: tensorout
        :return: list, or numpy.array
        """
        action_list = []
        return action_list

    @abstractmethod
    def step_rl(self, time_elapse, situation, action_dict):
        """
        强化学习子类实现，进行每步决策对抗推演，接收强化学习输出的指令驱动装备执行指令;
        训练智能体时每个强化学习描述每步决策调用一次，配置多单元的多智能体强化学习算法中，每个单元算一个智能体，
        不是每个智能体被调用一次，请在函数里实现所有多智能体的动作调用。
        推理应用时，此函数可放在step函数调用过程中被调用。
        实现示例参考agent/rl_gent/fighter/Fighter.py
        :param time_elapse:int, 推演仿真时间，单位：秒，取值0-推演总时间秒数
        :param situation: tuple, 单元字典和探测到的目标字典, units dict, contacts dict
        :param action_dict: dict. 所有智能体动作输出.
        :return:
        """
        pass

    def initial(self, situation):
        """
        智能体初始化, 可每局推演初始化变量，可赛前规划，可以用于创建任务，修改任务，设置条令，设置作战单元雷达开关机等
        智能体训练和推理应用（客户端中导入使用）中每局开始运行智能体，都会被调用一次；
        配置多单元的多智能体强化学习算法中，每局每个强化学习描述仅被调用一次，而不是每个智能体都被调用。
        :param situation: tuple: 单元字典和探测到的目标字典, units dict, contacts dict
        :return:
        """
        pass

    def deduction_end(self):
        """
        一局推演结束后，调用的函数，可用于保存模型等
        配置多单元的多智能体强化学习算法中，每局每个强化学习描述仅被调用一次，而不是每个智能体都被调用。
        """
        pass

    def get_model_out(self, obs):
        """
        神经网络前向过程, 可由子类实现，并在智能体推理应用中被客户端调用step函数中使用
        实现示例参考agent/rl_gent/fighter/Fighter.py
        :param obs: can be list, 观测, obs_trans函数的输出
        :return: tensorout, action函数的输入
        """
        pass

    @abstractmethod
    def load_model(self):
        """
        加载神经网络模型, 可自动搜寻脚本路径下的'model.h5'文件，用户可复写此函数，用于客户端调度时（推理应用时）被自动调用。
        实现示例参考agent/rl_gent/fighter/Fighter.py
        :return: model
        """
        pass

    @abstractmethod
    def act_trans(self, action_array, env_info: dict = None) -> ActionExe:
        """
        基于博弈算法框架输出的动作进行动作指令转换，转换为可读的指令信息，辅助下发动作指令给灵弈智能推演系统
        注意：强化学习智能体需实现此函数, 规则智能体无需实现.
        配置多单元的多智能体强化学习算法中，每个单元算一个智能体，每步决策调用一次每个智能体此函数。
        实现示例参考agent/rl_gent/fighter/Fighter.py
        :param action_array: list or ActionArray 训练框架输出的智能体决策动作数据
        :param env_info: 环境信息，tuple, 单元字典和探测到的目标字典, units dict, contacts dict
        :return: dict, agent_act_trans：转换后的动作指令辅助信息
        """
        agent_action_dict: dict = {}
        return agent_action_dict

    @abstractmethod
    def obs_trans(self, current_obs) -> ObsArray:
        """
        智能体状态信息转换, 从灵弈系统的可解释态势转换为智能体训练框架可接受的训练数据。
        注意：强化学习智能体需实现此函数, 规则智能体无需实现
        配置多单元的多智能体强化学习算法中，每个单元算一个智能体，每步决策调用一次每个智能体此函数。
        实现示例参考agent/rl_gent/fighter/Fighter.py
        :param current_obs: 环境信息，tuple, 单元字典和探测到的目标字典, units dict, contacts dict
        :return: list, agent_obs：智能体的状态信息
        """
        agent_obs: list = []
        return agent_obs

    @abstractmethod
    def get_reward(self, *args, **kwargs) -> float:
        """
        获取智能体的奖励, 推理应用阶段，不会被调用
        注意：强化学习智能体需实现此函数, 规则智能体无需实现
        配置多单元的多智能体强化学习算法中，每个单元算一个智能体，每步决策调用一次每个智能体此函数。
        智能体"check_terminated"函数返回True后，会仅再调用一次此奖励计算函数。
        实现示例参考agent/rl_gent/fighter/Fighter.py
        :return: float, reward：智能体的奖励值
        """
        own_obs, enemy_obs, last_own_obs, last_enemy_obs, action_dict = args  # 智能体当前态势，前一步态势，动作
        reward: float = 0.0
        return reward

    def check_terminated(self, obs) -> bool:
        """
        判定智能体状态是否结束, 推理应用阶段，不会被调用。
        注意：强化学习智能体需实现此函数, 规则智能体无需实现
        配置多单元的多智能体强化学习算法中，每个单元算一个智能体，每步决策调用一次每个智能体此函数。
        强化学习算法训练中，所有智能体此函数返回True,则此局推演中止训练，进入下一局。
        实现示例参考agent/rl_gent/fighter/Fighter.py
        :param obs: tuple, 环境数据信息，例: 单元字典和探测到的目标字典, units dict, contacts dict
        :return: bool, 智能体的是否需要终止状态信息
        """
        terminated_status: bool = False
        return terminated_status

    def is_done(self):
        """
        判定整局推演是否结束，一般由全局规则智能体判断，或全部强化学习单元都被摧毁后等.
        注意：config.py中配置的“get_server_config”函数"training"配置为True才会被调用。
        配置多单元的多智能体强化学习算法中，也每局每个强化学习描述仅被调用一次，而不是每个智能体被调用一次。
        当有智能体返回True(不管规则还是强化学习)，此局推演中止训练，进入下一局。
        :return: bool, 训练过程中是否需要本局推演结束，进行下局推演
        """
        return False


class RuleAgentBase(Player):
    """
    规则智能体基类
    """
    def __init__(self, side_name):
        """# 用户接口类初始化"""
        super(RuleAgentBase, self).__init__(side_name)
        # 智能体动态参数，训练时由配置config.py配置，客户端上推演使用调度功能动态配置
        self.agents_list = []  # 规则智能体对象，或强化学习智能体数据对象

    def step(self, time_elapse, situation):
        """
        规则智能体子类实现，进行每步对抗推演
        :param time_elapse:int, 推演仿真时间，单位：秒，取值0-推演总时间秒数
        :param situation: tuple, units list, contacts list
        :return:
        """
        pass

    def initial(self, situation):
        """
        智能体初始化, 可每局推演初始化变量，可赛前规划，可以用于创建任务，修改任务，设置条令，设置作战单元雷达开关机等
        :param situation: tuple: units, contacts
        :return:
        """
        pass

    def deduction_end(self):
        """一局推演结束后，调用的函数，可用于保存数据等"""
        pass

    def is_done(self):
        """
        判定整局推演是否结束，一般由全局规则智能体判断，或全部强化学习单元都被摧毁后等
        训练时，config.py中training为True时会调用；客户端应用智能体时，不会被调用
        :return: bool, 训练过程中是否需要本局推演结束，进行下局推演
        """
        return False
