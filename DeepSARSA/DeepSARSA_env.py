import time
import numpy as np
import tkinter as tk
from PIL import ImageTk, Image

PhotoImage = ImageTk.PhotoImage
UNIT = 90
HEIGHT = 6
WIDTH = 8

class Env(tk.Tk) :
    def __init__(self, render_speed = 0.01) :
        super(Env, self).__init__()
        self.render_speed = render_speed
        self.action_space = ['u', 'd', 'l', 'r']
        self.n_actions = len(self.action_space)
        self.title('DeepSARSA')
        self.geometry('{0}x{1}'.format(WIDTH * UNIT + 60, HEIGHT * UNIT + 70))
        self.shapes = self.load_images()
        self.canvas = self._build_canvas()

        

        self.counter = 0
        self.rewards = []
        self.goal = []

        # 고스트 지점
        self.set_reward([2, 2], -1)
        self.set_reward([6, 3], -1)
        self.set_reward([5, 4], -1)

        # 벽 지점
        self.set_reward([3, 0], -1)
        self.set_reward([4, 0], -1)
        self.set_reward([5, 0], -1)
        self.set_reward([6, 0], -1)
        self.set_reward([5, 1], -1)
        self.set_reward([0, 3], -1)
        self.set_reward([0, 4], -1)
        self.set_reward([0, 5], -1)
        self.set_reward([1, 5], -1)
        self.set_reward([2, 4], -1)
        self.set_reward([2, 5], -1)
        self.set_reward([3, 5], -1)

        # goal 인 지점
        self.set_reward([7, 5], 1)

    def load_images(self):
        background = PhotoImage(Image.open("./img/guard.png").resize((WIDTH * UNIT + 60, HEIGHT * UNIT + 70)))
        rectangle = PhotoImage(
            Image.open("./img/packman.png").resize((90, 90)))
        ghost1 = PhotoImage(
            Image.open("./img/ghost2.png").resize((90, 90)))
        ghost2 = PhotoImage(
            Image.open("./img/ghost3.png").resize((90, 90)))
        ghost3 = PhotoImage(
            Image.open("./img/ghost4.png").resize((90, 90)))  
        circle = PhotoImage(
            Image.open("./img/end2.png").resize((90, 90)))
        wall = PhotoImage(
            Image.open("./img/wall.png").resize((80, 80)))

        return background, rectangle, circle, ghost1, ghost2, ghost3, wall

    def _build_canvas(self):
        self.label=tk.Label(self, image=self.shapes[0])
        canvas = tk.Canvas(self, bg='gray15',
                           height=HEIGHT * UNIT,
                           width=WIDTH * UNIT)

        # 캔버스에 이미지 추가
        self.rectangle = canvas.create_image(45, 45, image=self.shapes[1])
        # self.circle = canvas.create_image(675, 495, image=self.shapes[2])
        # self.ghost1 = canvas.create_image(45, 495, image=self.shapes[3])
        # self.ghost2 = canvas.create_image(495, 405, image=self.shapes[4])
        # self.ghost3 = canvas.create_image(405, 45, image=self.shapes[5])
        # self.wall1 = canvas.create_image(315, 45, image=self.shapes[6])
        # self.wall2 = canvas.create_image(315, 135, image=self.shapes[6])
        # self.wall3 = canvas.create_image(405, 135, image=self.shapes[6])
        # self.wall4 = canvas.create_image(495, 135, image=self.shapes[6])
        # self.wall5 = canvas.create_image(585, 135, image=self.shapes[6])
        # self.wall6 = canvas.create_image(495, 225, image=self.shapes[6])
        # self.wall7 = canvas.create_image(45, 315, image=self.shapes[6])
        # self.wall8 = canvas.create_image(135, 315, image=self.shapes[6])
        # self.wall9 = canvas.create_image(405, 405, image=self.shapes[6])
        # self.wall10 = canvas.create_image(315, 495, image=self.shapes[6])
        # self.wall11 = canvas.create_image(405, 495, image=self.shapes[6])
        # self.wall12 = canvas.create_image(495, 495, image=self.shapes[6])
        
        
        # 그리드 생성
        for c in range(0, WIDTH * UNIT, UNIT):  # 0~400 by 80
            x0, y0, x1, y1 = c, 0, c, HEIGHT * UNIT
            canvas.create_line(x0, y0, x1, y1, fill='white')
        for r in range(0, HEIGHT * UNIT, UNIT):  # 0~400 by 80
            x0, y0, x1, y1 = 0, r, WIDTH * UNIT, r
            canvas.create_line(x0, y0, x1, y1, fill='white')


        self.label.place(x=0, y=0,width = WIDTH * UNIT + 60, height = HEIGHT * UNIT + 70)
        # 캔버스 가운데 정렬
        canvas.pack(anchor=tk.CENTER, expand=True)
        

        return canvas

    def reset_reward(self) :

        for reward in self.rewards :
            self.canvas.delete(reward['figure'])

        self.rewards.clear()
        self.goal.clear()

        # 고스트 지점
        self.set_reward([2, 2], -1)
        self.set_reward([6, 3], -1)
        self.set_reward([5, 4], -1)

        # 벽 지점
        self.set_reward([3, 0], -1)
        self.set_reward([4, 0], -1)
        self.set_reward([5, 0], -1)
        self.set_reward([6, 0], -1)
        self.set_reward([5, 1], -1)
        self.set_reward([0, 3], -1)
        self.set_reward([0, 4], -1)
        self.set_reward([0, 5], -1)
        self.set_reward([1, 5], -1)
        self.set_reward([2, 4], -1)
        self.set_reward([2, 5], -1)
        self.set_reward([3, 5], -1)

        # goal 인 지점
        self.set_reward([7, 5], 1)

    def set_reward(self, state, reward) :
        state = [int(state[0]), int(state[1])]

        x = int(state[0])
        y = int(state[1])

        X , Y = (UNIT * x) + UNIT / 2, (UNIT * y) + UNIT / 2

        temp = {}

        if reward > 0 :
            temp['reward'] = reward
            temp['figure'] = self.canvas.create_image(X, Y, image=self.shapes[2])

            self.goal.append(temp['figure'])

        elif reward < 0 :
            temp['direction'] = -1
            temp['reward'] = reward
            
            if [x, y] == [2, 2] :
                temp['figure'] = self.canvas.create_image(X, Y, image = self.shapes[3])
            elif [x, y] == [6, 3] :
                temp['figure'] = self.canvas.create_image(X, Y, image = self.shapes[4])
            
            elif [x, y] == [5, 4] :
                temp['figure'] = self.canvas.create_image(X, Y, image = self.shapes[5])

            # 벽 이미지
            else :
                temp['direction'] = 0
                temp['figure'] = self.canvas.create_image(X, Y, image = self.shapes[6])

        temp['coords'] = self.canvas.coords(temp['figure'])
        temp['state'] = state

        self.rewards.append(temp)

    def check_if_reward(self, state) :
        check_list = dict()
        check_list['if_goal'] = False
        rewards = 0

        for reward in self.rewards :
            if reward['state'] == state :
                rewards += reward['reward']
                if reward['reward'] == 1 :
                    check_list['if_goal'] = True

        check_list['rewards'] = rewards

        return check_list

    def coords_to_state(self, coords) :
        x = int((coords[0] - UNIT / 2) / UNIT)
        y = int((coords[1] - UNIT / 2) / UNIT)

        return [x, y]

    def reset(self) :
        self.render()

        x, y = self.canvas.coords(self.rectangle)

        self.canvas.move(self.rectangle, UNIT / 2 - x, UNIT / 2 - y)
        self.reset_reward()

        return self.get_state()

    def step(self, action) :
        self.counter += 1
        self.render()

        if self.counter % 2 == 1 :
            self.rewards = self.move_rewards()

        next_coords = self.move(self.rectangle, action)
        check = self.check_if_reward(self.coords_to_state(next_coords))

        done = check['if_goal']
        reward = check['rewards']

        self.canvas.tag_raise(self.rectangle)

        s_ = self.get_state()

        return s_, reward, done

    def move_rewards(self) :
        new_rewards = []
        for temp in self.rewards :
            if temp['reward'] == 1 :
                new_rewards.append(temp)
                continue

            temp['coords'] = self.move_const(temp)
            temp['state'] = self.coords_to_state(temp['coords'])
            
            new_rewards.append(temp)

        return new_rewards

    def move_const(self, target) :
        s = self.canvas.coords(target['figure'])

        wall_list = []
        # print(self.rewards)
        for reward in self.rewards :
            if 'direction' in reward and reward['direction'] == 0 :
                x, y = reward['coords'][0] + UNIT , reward['coords'][1]
                wall_list.append([x, y])
                # wall_list.append(reward['coords'])

        # for _ in wall_list :
        #     print(_)

        base_action = np.array([0, 0])

        if target['direction'] != 0 :
            if s[0] == (WIDTH - 1) * UNIT + UNIT / 2 :
                target['direction'] = 1

            elif s[0] == UNIT / 2 or (s in wall_list) :
                target['direction'] = -1

        if target['direction'] == -1 :
            base_action[0] += UNIT
        elif target['direction'] == 1 :
            base_action[0] -= UNIT

        self.canvas.move(target['figure'], base_action[0], base_action[1])

        s_ = self.canvas.coords(target['figure'])

        return s_

    def move(self, target, action) :
        s = self.canvas.coords(target)

        base_action = np.array([0, 0])

        if action == 0 :
            if s[1] > UNIT :
                base_action[1] -= UNIT
        
        elif action == 1 :
            if s[1] < (HEIGHT - 1) * UNIT:
                base_action[1] += UNIT

        elif action == 2 :
            if s[0] < (WIDTH - 1) * UNIT :
                base_action[0] += UNIT
        
        elif action == 3 :
            if s[0] > UNIT :
                base_action[0] -= UNIT

        self.canvas.move(target, base_action[0], base_action[1])

        s_ = self.canvas.coords(target)

        return s_

    def get_state(self) :
        location = self.coords_to_state(self.canvas.coords(self.rectangle))

        agent_x = location[0]
        agent_y = location[1]

        states = list()

        for reward in self.rewards :
            reward_location = reward['state']
            states.append(reward_location[0] - agent_x)
            states.append(reward_location[1] - agent_y)

            if reward['reward'] < 0 :
                states.append(-1)
                states.append(reward['direction'])
            
            else :
                states.append(1)

        return states

    
    def render(self) :
        time.sleep(self.render_speed)
        self.update()


        
    


if __name__ == '__main__' :
    env = Env()

    # env.test()
    # for _ in range(15):
    #     time.sleep(0.5)
    #     env.move_rewards()
    #     env.render()

    env.mainloop()