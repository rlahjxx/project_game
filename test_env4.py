import time
import numpy as np
import tkinter as tk
from PIL import ImageTk, Image

np.random.seed(1)
PhotoImage = ImageTk.PhotoImage
UNIT = 60  # 픽셀 수
HEIGHT = 8  # 그리드월드 세로
WIDTH = 16  # 그리드월드 가로


class Env(tk.Tk):
    def __init__(self):
        super(Env, self).__init__()
        self.action_space = ['u', 'd', 'l', 'r']
        self.n_actions = len(self.action_space)
        self.title('Q Learning')
        self.geometry('{0}x{1}'.format(WIDTH * UNIT + 60, HEIGHT * UNIT + 70))
        self.shapes = self.load_images()
        self.canvas = self._build_canvas()
        self.texts = []

    def _build_canvas(self):
        self.label=tk.Label(self, image=self.shapes[0])
        canvas = tk.Canvas(self, bg='gray15',
                           height=HEIGHT * UNIT,
                           width=WIDTH * UNIT)

        # 캔버스에 이미지 추가
        self.rectangle = canvas.create_image(30, 30, image=self.shapes[1])
        self.circle = canvas.create_image(930, 450, image=self.shapes[2])
        self.ghost1 = canvas.create_image(210, 150, image=self.shapes[3])
        self.ghost2 = canvas.create_image(210, 210, image=self.shapes[4])
        self.ghost3 = canvas.create_image(450, 270, image=self.shapes[5])
        
        
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

    def load_images(self):
        background = PhotoImage(Image.open("../img/guard.png").resize((WIDTH * UNIT + 60, HEIGHT * UNIT + 70)))
        rectangle = PhotoImage(
            Image.open("../img/packman.png").resize((60, 60)))
        ghost1 = PhotoImage(
            Image.open("../img/ghost2.png").resize((60, 60)))
        ghost2 = PhotoImage(
            Image.open("../img/ghost3.png").resize((60, 60)))
        ghost3 = PhotoImage(
            Image.open("../img/ghost4.png").resize((60, 60)))  
        circle = PhotoImage(
            Image.open("../img/end2.png").resize((60, 60)))

        return background, rectangle, circle, ghost1, ghost2, ghost3

    def text_value(self, row, col, contents, action, font='Helvetica', size=7,
                   style='normal', anchor="nw"):

        if action == 0:
            origin_x, origin_y = 4, 26
        elif action == 1:
            origin_x, origin_y = 50, 26
        elif action == 2:
            origin_x, origin_y = 26, 4
        else:
            origin_x, origin_y = 26, 50

        x, y = origin_y + (UNIT * col), origin_x + (UNIT * row)
        font = (font, str(size), style)
        text = self.canvas.create_text(x, y, fill="white", text=contents,
                                       font=font, anchor=anchor)
        return self.texts.append(text)

    def print_value_all(self, q_table):
        for i in self.texts:
            self.canvas.delete(i)
        self.texts.clear()
        for x in range(WIDTH):
            for y in range(HEIGHT):
                for action in range(0, 4):
                    state = [x, y]
                    if str(state) in q_table.keys():
                        temp = q_table[str(state)][action]
                        self.text_value(y, x, round(temp, 3), action)

    def coords_to_state(self, coords):
        x = int((coords[0] - 30) / 60)
        y = int((coords[1] - 30) / 60)
        return [x, y]

    def reset(self):
        self.update()
        time.sleep(0.5)
        x, y = self.canvas.coords(self.rectangle)
        self.canvas.move(self.rectangle, UNIT / 2 - x, UNIT / 2 - y)
        self.render()
        return self.coords_to_state(self.canvas.coords(self.rectangle))

    def step(self, action):
        state = self.canvas.coords(self.rectangle)
        base_action = np.array([0, 0])
        self.render()

        if action == 0:  # 상
            if state[1] > UNIT:
                base_action[1] -= UNIT
        elif action == 1:  # 하
            if state[1] < (HEIGHT - 1) * UNIT:
                base_action[1] += UNIT
        elif action == 2:  # 좌
            if state[0] > UNIT:
                base_action[0] -= UNIT
        elif action == 3:  # 우
            if state[0] < (WIDTH - 1) * UNIT:
                base_action[0] += UNIT

        # 에이전트 이동
        self.canvas.move(self.rectangle, base_action[0], base_action[1])
        # 에이전트(빨간 네모)를 가장 상위로 배치
        self.canvas.tag_raise(self.rectangle)
        next_state = self.canvas.coords(self.rectangle)

        # 보상 함수
        if next_state == self.canvas.coords(self.circle):
            reward = 100
            done = True
        elif next_state in [self.canvas.coords(self.ghost1),
                            self.canvas.coords(self.ghost2)]:
            reward = -100
            done = True
        else:
            reward = 0
            done = False

        next_state = self.coords_to_state(next_state)
        return next_state, reward, done

    def render(self):
        time.sleep(0.05)
        self.update()
