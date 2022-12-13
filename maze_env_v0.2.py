import time
import numpy as np
import tkinter as tk
from PIL import ImageTk, Image
import make_maze

# 랜덤 미로 생성
map = make_maze.Maze()
# 랜덤 미로 배열 사이즈 변경
map.set_size(5)
# 배열로 값을 반환 받고
# 0 : 이동 가능 지점, 1: 벽 , 2 : 시작 지점, 3 : 종료 지점
map = map.get_mazeMap()

PhotoImage = ImageTk.PhotoImage
UNIT = 90
# 창 너비 , 높이 , 위치 설정 (한칸은 UNIT * UNIT 으로 설정)
WIDTH , HEIGHT = len(map[0]) , len(map)

# # 테스트 용도
# WIDTH, HEIGHT = 5,2
# print(WIDTH, HEIGHT)
# test = [[1,2,3,4,5],[6,7,8,9,10]]

################################
# 환경 구축
################################
class Env(tk.Tk) :
    def __init__(self) :
        super(Env, self).__init__()
        # 위 , 아래 , 왼쪽 , 오른쪽
        self.action_space = ['u', 'd', 'l', 'r']
        # 현재 환경에서 4개 중에 하나로 선택
        self.n_actions = len(self.action_space)
        # title 이름 설정
        self.title('Maze_MC')
        # tkinter (화면) 사이즈 설정
        self.geometry('{}x{}'.format(WIDTH * UNIT, HEIGHT * UNIT))
        # self.configure(bg='black') # 테스트 용도
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
            Image.open("./img/rectangle.png").resize((UNIT - resize, UNIT - resize)))
        triangle = PhotoImage(
            Image.open("./img/triangle.png").resize((UNIT - resize, UNIT - resize)))
        circle = PhotoImage(
            Image.open("./img/circle.png").resize((UNIT - resize, UNIT - resize)))

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

        # # 좌표 찍기 test
        # # 행렬을 그림으로 표현하기 위해서는 x, height 으로 y 로 width 로 변경해야 한다.
        # for x in range(HEIGHT) :
        #     for y in range(WIDTH) :
        #         # state = [x, y]
        #         print(x, type(x))
        #         label = tk.Label(self, text = str(test[x][y]))
        #         label.place(x = (UNIT/2) + (UNIT * y), y = (UNIT/2) + (UNIT * x))

        # 행렬을 그림으로 표현하기 위해서는 x, height 으로 y 로 width 로 변경해야 한다.
        # print(map)
        for h in range(HEIGHT) :
            for w in range(WIDTH) :
                # 벽 지점 이미지 삽임
                if map[h][w] == 1 :
                    # 직접 rectangle 그리기
                    # canvas.create_rectangle(w * UNIT, h * UNIT, w * UNIT + UNIT, h * UNIT + UNIT, fill="gray")
                    
                    # 이미지 삽입
                    self.rectangle = canvas.create_image((UNIT / 2) + (UNIT * w), (UNIT / 2) + (UNIT * h), image = self.shapes[0])

                # 시작 지점 이미지 삽입
                elif map[h][w] == 2 :
                    self.triangle = canvas.create_image((UNIT / 2) + (UNIT * w), (UNIT / 2) + (UNIT * h), image = self.shapes[1])
                    # 초기 시작 위치 w,h 기억하는 변수 선언
                    self.W_start_point , self.H_start_point= (UNIT / 2) + (UNIT * w) , (UNIT / 2) + (UNIT * h)

                # 종료 지점 이미지 삽입
                elif map[h][w] == 3 :
                    self.circle = canvas.create_image((UNIT / 2) + (UNIT * w), (UNIT / 2) + (UNIT * h), image = self.shapes[2])
        
        # canvas.pack(anchor=tk.CENTER, expand=True)
        canvas.pack()
        return canvas
    #####################

    #####################
    # 강화학습 결과를 불러오는 함수 - main 으로 부터 value_table 을 넘겨 받는다.
    def print_value_all(self, value_table) :
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
                state = [h, w] # key 값이 ex) [2,3] 형태로 되어 있다.

                #####################
                # 몬테카를로 결과는 상태 가치 한개만 반환된다.
                if str(state) in value_table.keys() :
                    # 임시 변수 temp 에 저장 한다. 올림 하기 위해서 사용한다.
                    temp = value_table[str(state)]

                    # state 통해서 해당 지역(ex) [2,3]) 의 가중치를 찍기 위해서 w, h 를 넘겨준다.
                    self.text_value(w, h, round(temp, 3))
                #####################


    #####################

    #####################
    # print_value_all() 함수로 부터 넘겨받은 행과 열로 가중치 출력 함수
    def text_value(self, w, h, value, font = 'Helvetica', size = 10, style = 'normal', anchor = 'nw'):
        # 처음 출력되는 위치 표시, 왼쪽 하단으로 설정
        origin_w, origin_h = UNIT - 30 , UNIT - 20

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
        self.update()
        # 업데이트 후 시간 텀
        time.sleep(0.5)

        # 현재 triangle 을 w, h 위치 반환
        w, h = self.canvas.coords(self.triangle)

        # 이동된 triangle 을 초기 위치로 이동, triangle 을 (W_start_poing - w, H_start_point - h) 만큼 이동시킨다.
        self.canvas.move(self.triangle, self.W_start_point - w, self.H_start_point - h)

        # render 함수를 통해서 업데이트 진행
        self.render()
        time.sleep(1)

        # coords_to_state() 함수를 통해서 (width, hight) -> (w, h) 로 변환해준다.
        return self.coords_to_state([self.W_start_point, self.H_start_point])
    #####################

    #####################
    #  (width, hight) -> (w, h) 로 변환해주는 함수 선언
    def coords_to_stats(self, coords) :
        w, h = int((coords[0] - (UNIT / 2)) / UNIT), int((coords[1] - (UNIT / 2)) / UNIT)
        return [w, h]
    #####################

    #####################
    # triangle 한 스탭 마다 위치 변경 함수
    def step(self, action) :
        # (width, hight) 를 저장하는 state 변수 선언
        state = self.canvas.coords(self.triangle)
        # 이동 할 거리를 표시할 base_action 변수 선언
    #####################


        



if __name__ == '__main__' :
    env = Env()
    # window=tk.Tk()

    # env.text_value(2,5,10)

    # env.reset()

    w , h = env.coords_to_stats([env.W_start_point, env.H_start_point])

    print(w, h)

    env.mainloop()