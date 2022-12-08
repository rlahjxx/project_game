import copy
import pylab
import random
import numpy as np
from DeepSARSA_env import Env
import tensorflow as tf
import time


class DeepSARSA(tf.keras.Model) :
    def __init__(self, action_size) :
        super(DeepSARSA, self).__init__()
        self.fc1 = tf.keras.layers.Dense(30, activation='relu')
        self.fc2 = tf.keras.layers.Dense(30, activation='relu')
        self.fc_out = tf.keras.layers.Dense(action_size)

    def call(self, input) :
        x = self.fc1(input)
        x = self.fc2(x)
        q = self.fc_out(x)

        return q

class DeepSARSAgent :
    def __init__(self, state_size, action_size) :
        self.state_size = state_size
        self.action_size = action_size

        self.discount_factor = 0.99
        self.learning_rate = 0.001
        self.epsilon = 1.
        # self.epsilon = 0.01  
        self.epsilon_decay = .9999
        self.epsilon_min = 0.01
        self.model = DeepSARSA(self.action_size)
        self.optimizer = tf.keras.optimizers.Adam(lr=self.learning_rate)

    def get_action(self, state):
        if np.random.rand() <= self.epsilon:
            return random.randrange(self.action_size)
        else:
            q_values = self.model(state)
            return np.argmax(q_values[0])

    def train_model(self, state, action, reward, next_state, next_action, done):
        if self.epsilon > self.epsilon_min:
            self.epsilon *= self.epsilon_decay

        # 학습 파라메터
        model_params = self.model.trainable_variables
        # 역전파 과정
        with tf.GradientTape() as tape:
            tape.watch(model_params)
            predict = self.model(state)[0]
            one_hot_action = tf.one_hot([action], self.action_size)
            predict = tf.reduce_sum(one_hot_action * predict, axis=1)

            # done = True 일 경우 에피소드가 끝나서 다음 상태가 없음
            next_q = self.model(next_state)[0][next_action]
            # 정답
            target = reward + (1 - done) * self.discount_factor * next_q

            # MSE 오류 함수 계산
            loss = tf.reduce_mean(tf.square(target - predict))
        
        # 오류함수를 줄이는 방향으로 모델 업데이트
        grads = tape.gradient(loss, model_params) # 각 가중치의 오차(업데이트할 가중치들의 값)를 보여줌
        # 오차 역전파를 통해 각 가중치를 업데이트함
        self.optimizer.apply_gradients(zip(grads, model_params))

if __name__ == '__main__' :
    env = Env(render_speed=0.01)
    state_size = 63
    action_space = [0, 1, 2, 3, 4]
    action_size = len(action_space)
    agent = DeepSARSAgent(state_size, action_size)

    scores, episodes = [], []

    EPISODES = 1000

    for e in range(EPISODES):
        done = False
        score = 0
        # env 초기화
        state = env.reset()
        state = np.reshape(state, [1, state_size])

        while not done:
            # 현재 상태에 대한 행동 선택
            action = agent.get_action(state)

            # 선택한 행동으로 환경에서 한 타임스텝 진행 후 샘플 수집
            next_state, reward, done = env.step(action)
            next_state = np.reshape(next_state, [1, state_size])
            next_action = agent.get_action(next_state)

            # 샘플로 모델 학습
            agent.train_model(state, action, reward, next_state, 
                                next_action, done)
            score += reward
            state = next_state

            if done:
                # 에피소드마다 학습 결과 출력
                print("episode: {:3d} | score: {:3d} | epsilon: {:.3f}".format(
                      e, score, agent.epsilon))

                scores.append(score)
                episodes.append(e)
                pylab.plot(episodes, scores, 'b')
                pylab.xlabel("episode")
                pylab.ylabel("score")
                pylab.savefig("./save_graph/graph.png")


        # 100 에피소드마다 모델 저장
        if e % 100 == 0:
            agent.model.save_weights('save_model/model', save_format='tf')