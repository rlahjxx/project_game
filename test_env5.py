import time
import numpy as np
import tkinter as tk
from PIL import ImageTk, Image

# 랜덤 미로 생성
map = [[2,0,1,0,0,0], [0,0,1,0,0,0], [0,0,1,0,1,0], [0,0,0,0,0,0], [0,0,0,1,0,0], [1,0,0,1,0,3]]
# 0 : 이동 가능 지점, 1: 벽 , 2 : 시작 지점, 3 : 종료 지점

PhotoImage = ImageTk.PhotoImage
UNIT = 90
# 창 너비 , 높이 , 위치 설정 (한칸은 UNIT * UNIT 으로 설정)
WIDTH , HEIGHT = len(map[0]) , len(map)

################################
# 환경 구축
################################
class Env(tk.Tk) :
    def __init__(self) :
        super(Env, self).__init__()
        self.UNIT, self.WIDTH, self.HEIGHT = UNIT, WIDTH, HEIGHT
        # 위 , 아래 , 왼쪽 , 오른쪽
        self.action_space = ['u', 'd', 'l', 'r']
        # 현재 환경에서 4개 중에 하나로 선택
        self.n_actions = len(self.action_space)
        # title 이름 설정
        self.title('Maze_Q')
        # tkinter (화면) 사이즈 설정
        self.geometry('{}x{}'.format(WIDTH * UNIT, HEIGHT * UNIT))
        # 모든 이미지를 load_images() 함수를 통해서 shapes 에 저장
        self.shapes = self.load_images()
        # 화면 그릴 창 canvas 생성 (_build_canvas() 함수 사용)
        self.canvas = self._build_canvas()
        # 화면에 가치를 표시하기 위해서 변수 선언 (임시 변수다, 항상 새로운 결과값으로 대체 된다.)
        self.texts = []

    #####################
    # 이미지 불러오는 함수
    def load_images(self) :
        # 사이즈 조정을 위한 변수 선언
        resize = 10

        rectangle = PhotoImage(
            Image.open("../img/rectangle.png").resize((UNIT - resize, UNIT - resize)))
        triangle = PhotoImage(
            Image.open("../img/triangle.png").resize((UNIT - resize, UNIT - resize)))
        circle = PhotoImage(
            Image.open("../img/circle.png").resize((UNIT - resize, UNIT - resize)))

        return rectangle , triangle , circle
    #####################

    #####################
    # canvas 부분 생성
    def _build_canvas(self) :
        canvas = tk.Canvas(self, bg = 'white', height = HEIGHT * UNIT, width = WIDTH * UNIT)

        # 세로선 그리기 - x 좌표는 고정 하고 y 좌표를 0부터 끝까지로 할당해서 그린다.
        for c in range(0, WIDTH * UNIT , UNIT) :
            x0, y0, x1, y1 = c , 0 , c , HEIGHT * UNIT
            canvas.create_line(x0, y0, x1, y1)
        
        # 가로선 그리기 - y 좌표는 고정 하고 x 좌표를 0부터 끝까지로 할당해서 그린다.
        for r in range(0, HEIGHT * UNIT, UNIT) :
            x0, y0, x1, y1 = 0, r, WIDTH * UNIT , r
            canvas.create_line(x0, y0, x1, y1)

        # 행렬을 그림으로 표현하기 위해서는 x, height 으로 y 로 width 로 변경해야 한다.
        self.rectangle = []
        for h in range(HEIGHT) :
            for w in range(WIDTH) :
                # 벽 지점 이미지 삽임
                if map[h][w] == 1 :
                    # 직접 rectangle 그리기
                    # canvas.create_rectangle(w * UNIT, h * UNIT, w * UNIT + UNIT, h * UNIT + UNIT, fill="gray")
                    
                    # 이미지 삽입
                    # self.rectangle = canvas.create_image((UNIT / 2) + (UNIT * w), (UNIT / 2) + (UNIT * h), image = self.shapes[0])
                    self.rectangle.append(canvas.create_image((UNIT / 2) + (UNIT * w), (UNIT / 2) + (UNIT * h), image = self.shapes[0]))

                # 시작 지점 이미지 삽입
                elif map[h][w] == 2 :
                    self.triangle = canvas.create_image((UNIT / 2) + (UNIT * w), (UNIT / 2) + (UNIT * h), image = self.shapes[1])
                    # 초기 시작 위치 w,h 기억하는 변수 선언
                    self.W_start_point , self.H_start_point= (UNIT / 2) + (UNIT * w) , (UNIT / 2) + (UNIT * h)

                # 종료 지점 이미지 삽입
                elif map[h][w] == 3 :
                    self.circle = canvas.create_image((UNIT / 2) + (UNIT * w), (UNIT / 2) + (UNIT * h), image = self.shapes[2])
                
        
        canvas.pack()
        return canvas
    #####################

    #####################
    # 강화학습 결과를 불러오는 함수 - main 으로 부터 value_table 을 넘겨 받는다.
    def print_value_all(self, q_table) :
        # 기존 canvas 에 작성되어 있는 결과값 지우기
        # 출력 결과창을 위해 사용한 변수 texts 를 이용
        for _ in self.texts :
            self.canvas.delete(_)
        # texts 변수 지우기
        self.texts.clear()

        # 결과값 가지고 오기
        for h in range(HEIGHT) :
            for w in range(WIDTH) :
                # 결과값이 dict 로 들어온다. 그걸 위해서 state 저장
                for action in range(0, 4):
                    state = [w, h] # key 값이 ex) [2,3] 형태로 되어 있다.
                    if str(state) in q_table.keys():
                        # 임시 변수 temp 에 저장 한다. 올림 하기 위해서 사용한다.
                        temp = q_table[str(state)][action]
                        # state 통해서 해당 지역(ex) [2,3]) 의 가중치를 찍기 위해서 w, h 를 넘겨준다.
                        self.text_value(w, h, round(temp, 3), action)

    #####################

    #####################
    # print_value_all() 함수로 부터 넘겨받은 행과 열로 가중치 출력 함수
    def text_value(self, w, h, value, action, font = 'Helvetica', size = 10, style = 'normal', anchor = 'nw'):
        # 처음 출력되는 위치 표시, 왼쪽 하단으로 설정
        if action == 0:
            origin_w, origin_h = 4, 26
        elif action == 1:
            origin_w, origin_h = 50, 26
        elif action == 2:
            origin_w, origin_h = 26, 4
        else:
            origin_w, origin_h = 26, 50
#         origin_w, origin_h = UNIT - 30 , UNIT - 20

        # 출력 되는 위치 표시
        w , h = origin_w + (UNIT * w) , origin_h + (UNIT * h)

        # 폰트 설정
        font = (font, str(size), style)

        # 출력 후 text 변수에 저장
        text = self.canvas.create_text(w, h, fill = 'black', text = value, font = font, anchor = anchor)
        
        # 출력된 값 texts 변수에 저장
        self.texts.append(text)
    #####################

    #####################
    # triangle 의 위치를 처음 위치로 되될리기
    def reset(self) :

        # 프레임 업데이트 하는 함수 호출
        self.render()

        # 현재 triangle 을 w, h 위치 반환
        w, h = self.canvas.coords(self.triangle)

        # 이동된 triangle 을 초기 위치로 이동, triangle 을 (W_start_poing - w, H_start_point - h) 만큼 이동시킨다.
        self.canvas.move(self.triangle, self.W_start_point - w, self.H_start_point - h)

        # render 함수를 통해서 업데이트 진행
        self.render()
        time.sleep(1)

        # coords_to_state() 함수를 통해서 (width, height) -> (w, h) 로 변환해준다.
        return self.coords_to_state([self.W_start_point, self.H_start_point])
    #####################

    #####################
    #  (width, height) -> (w, h) 로 변환해주는 함수 선언
    def coords_to_state(self, coords) :
        w, h = int((coords[0] - (UNIT / 2)) / UNIT), int((coords[1] - (UNIT / 2)) / UNIT)
        return [w, h]
    #####################

    #####################
    # triangle 한 스탭 마다 위치 변경 함수
    def step(self, action) :
        # (width, hight) 를 저장하는 state 변수 선언
        state = self.canvas.coords(self.triangle)
        # 이동 할 거리를 표시할 state_action 변수 선언
        state_action = np.array([0, 0])
        self.render()

        # 위쪽으로 이동
        if action == 0 : 
            # 위쪽으로 이동 가능 여부 확인, 한칸의 길이 UNIT 보다 크다면 이동 가능
            if state[1] > UNIT :
                state_action[1] -= UNIT # state_action = [0, - UNIT]
        # 아래쪽으로 이동
        elif action == 1 :
            # 아래쪽 이동 가능 여부 확인
            if state[1] < (HEIGHT - 1) * UNIT :
                state_action[1] += UNIT # state_action = [0, + UNIT]
        # 왼쪽으로 이동
        elif action == 2 :
            # 왼쪽 이동 가능 여부 확인
            if state[0] > UNIT :
                state_action[0] -= UNIT # state_action = [- UNIT , 0]
        # 오른쪽으로 이동
        elif action == 3 :
            # 오른쪽 이동 가능 여부 확인
            if state[0] < (WIDTH - 1) * UNIT :
                state_action[0] += UNIT # state_action = [+ UNIT, 0]

        # triangle 이동
        self.canvas.move(self.triangle, state_action[0], state_action[1])

        # triangle 이미지를 항상 상위 이미지로 보여준다
        self.canvas.tag_raise(self.triangle)

        #####################
        # 환경이 줄 보상을 설정
        # triangle 이동 한 후의 (width, height) 을 저장한 변수 next_state 선언
        next_state = self.canvas.coords(self.triangle)

        # 목표 지점에 도착 할 경우 보상 100 부여
        if next_state == self.canvas.coords(self.circle) :
            reward = 100
            done = True
        # 벽에 도착 할 경우 보상을 - 100 부여
        # elif next_state in self.canvas.coords(self.rectangle) :
        elif next_state in [self.canvas.coords(x) for x in self.rectangle] :
            print('보상 -100 부여')
            reward = -100
            done = True
        # 일반 길일 경우에 보상 0
        else :
            reward = 0
            done = False
        #####################

        # [w, h] , reward, done 을 반환 해준다.
        return self.coords_to_state(next_state), reward, done
    #####################

    #####################
    # undate 해주는 함수 선언
    def render(self) :
        time.sleep(0.03)
        self.update()
    #####################