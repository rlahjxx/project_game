import numpy as np
import random
from collections import defaultdict
from maze_env import Env
import time

# 환경 Env 로 부터 정보를 가지고 온다.
env = Env()
UNIT = env.UNIT
WIDTH = env.WIDTH
HEIGHT = env.HEIGHT

# 에이전트 몬테카를로 학습 알고리즘 적용 (모든 에피소드 각각의 샘플로 부터 학습)
class MCAgent :
    def __init__(self, actions) :
        # Env 로 부터 WIDTH, HEIGHT 값을 가지고 온다.
        self.width = WIDTH
        self.height = HEIGHT
        # 에이전트가 취할 행동 변수를 선언
        self.actions = actions
        # 학습률 변수 선언, 클수록 빠르게 변하지만 단점도 존재
        self.learning_rate = 0.01
        # 할인률 변수 설정
        self.discount_factor = 0.9
        # 입실론 변수 설정
        self.epsilon = 0.1
        # 에피소드를 저장할 변수 선언
        self.samples = []
        # 가치 함수 table 생성
        self.value_table = defaultdict(float)

    #####################
    # 에피소드를 저장하는 save_sample() 함수 선언 
    def save_sample(self, state, reward, done) :
        self.samples.append([state, reward, done])
    #####################

    #####################
    # 한 에피소드에서 방문한 모든 자리의 가치 함수를 업데이트
    def update(self) :
        G_t = 0
        visit_state = []

        for reward in reversed(self.samples) :
            state = str(reward[0])

            if state not in visit_state :
                visit_state.append(state)
                G_t = reward[1] + self.discount_factor * G_t
                value = self.value_table[state]
                self.value_table[state] = (value + self.learning_rate * (G_t - value))
    #####################

    def get_action(self, state) :
        if np.random.rand() < self.epsilon :
            action = np.random.choice(self.actions)
        else :
            next_state = self.possible_next_state(state)
            action = self.arg_max(next_state)

        return int(action) 

    @staticmethod
    def arg_max(next_state) :
        max_index_list = []
        max_value = next_state[0]
        for index, value in enumerate(next_state):
            if value > max_value:
                max_index_list.clear()
                max_value = value
                max_index_list.append(index)
            elif value == max_value:
                max_index_list.append(index)
        # print('max_index_list = ', max_index_list)
        return random.choice(max_index_list)

    def possible_next_state(self, state) :
        w, h = state
        next_state = [0.0] * 4

        if h != 0 :
            if str([w, h - 1]) in self.value_table :
                next_state[0] = self.value_table[str([w, h - 1])]
            else :
                next_state[0] = 0.0
        else :
            next_state[0] = self.value_table[str(state)]

        if h != self.height - 1 :
            if str([w, h + 1]) in self.value_table :
                next_state[1] = self.value_table[str([w, h + 1])]
            else :
                next_state[1] = 0.0
        else :
            next_state[1] = self.value_table[str(state)]

        if w != 0 :
            if str([w - 1, h]) in self.value_table :
                next_state[2] = self.value_table[str([w - 1, h])]
            else :
                next_state[2] = 0.0
        else :
            next_state[2] = self.value_table[str(state)]

        if w != self.width - 1 :
            if str([w + 1, h]) in self.value_table :
                next_state[3] = self.value_table[str([w + 1, h])]
            else :
                next_state[3] = 0.0
        else :
            next_state[3] = self.value_table[str(state)]

        return next_state




if __name__ == '__main__' :
    
    agent = MCAgent(actions=list(range(env.n_actions)))
    # state = [0,0]
    # action = agent.get_action(state)

    # # print(action)

    # env.render()

    # # next_state, reward, done = env.step(1)

    # # print(next_state)
    # print(agent.value_table)

    env.reset()
    env.render()
    time.sleep(3)

    for episode in range(100) :
        state = env.reset()
        action = agent.get_action(state)

        while True :
            env.render()
            next_state , reward, done = env.step(action)
            # time.sleep(0.5)
            # print('save_sample 전 : ',agent.value_table)
            agent.save_sample(next_state, reward, done)
            # print('save_sample 후 : ',agent.value_table)

            action = agent.get_action(next_state)

            if done :
                # print(f'episode 번째 : {episode}')
                agent.update()

                env.print_value_all(agent.value_table)

                env.print_label()

                agent.samples.clear()
                break

    state = env.reset()

    env.mainloop()