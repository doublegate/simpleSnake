import curses
import random
import sys


def show_message(message, color="white"):
    colors = {"red": 1, "green": 2, "yellow": 3, "blue": 4, "purple": 5, "cyan": 6, "white": 7}
    sys.stdout.write("\x1b[1;3{};40m{}\x1b[0m\n".format(colors[color], message))


def flatten_array(array):
    return [item for sublist in array for item in sublist]


height = 20
width = 41
max_steps = height * width // 3 - 1


class Game(object):
    def __init__(self):
        self.stdscr = curses.initscr()
        self.stdscr.nodelay(True)
        self.stdscr.keypad(True)
        self.window_shape = [[x + 1 if x >= 1 else 0 for x in range(-1, width)]
                             for _ in range(1, height + 1)]
        curses.curs_set(False)

        self.direction = (-1, 0)
        self.length = 3
        self.position = ((width // 2), (height // 2))
        self.food_positions = []

        self.score = 0
        self.high_score = 0
        self.last_step = None

        self._create_new_food()

    def _update_screen(self):
        self.stdscr.clear()
        for row in range(len(self.window_shape)):
            line = ""
            for column in range(len(self.window_shape[row])):
                line += str("##" if self.window_shape[row][column] == -1 else
                            '..' if (row == self.position[1] and
                                     column == self.position[0]) else
                            '@@' if self.window_shape[row][column] > -1 else
                            '  ')
            print(line[:width * 2])

        self.stdscr.addstr("\nSCORE: {}\nHIGHSCORE: {}".format(self.score,
                                                               self.high_score))

    def reset(self):
        delattr(self, '_instance')
        return Game.__new__(Game)

    @staticmethod
    def step(*args):
        pass

    def update_state(self):
        head_coords = list(map(sum, zip([i for i in self.position], self.direction)))
        new_head = tuple([head_coords[0] % width, head_coords[1] % height])

        self.window_shape[new_head[1]][new_head[0]] = len(self.food_positions) - 1 \
            if new_head not in self.food_positions \
            else -1

        if (new_head != self.position and
                new_head not in self.food_positions and
                (new_head[0] < 0 or new_head[0] >= width or
                 new_head[1] < 0 or new_head[1] >= height)):

            gameover = True
            score = self.score
            high_score = max(score, self.high_score)

            stdscr = self.stdscr
            curses.endwin()

            return gameover, score, high_score, stdscr

        elif new_head in self.food_positions:
            eaten = True
            while eaten:
                food = random.randint(0, len(self.food_positions) - 1)
                eaten = (self.food_positions[food] == new_head)
                if not eaten:
                    self.window_shape[self.food_positions[food][1]][
                        self.food_positions[food][0]] = 0
                    self.food_positions.pop(food)

            self.length += 1
            self._create_new_food()
            self.score += 1

            if self.high_score <= self.score:
                self.high_score = self.score

        else:
            tail = self.window_shape[self.position[1]][self.position[0]]

            if tail != -1:
                self.window_shape[self.position[1]][self.position[0]] = 0
                self.position = (self.position[0] -
                                 self.window_shape[self.position[1]].index(tail) *
                                 self.direction[0],
                                 self.position[1] -
                                 self.window_shape[self.position[1]].index(tail) *
                                 self.direction[1])

        self._update_screen()
        self.position = new_head

    def _create_new_food(self):
        free_space = sum(list(filter(lambda e: e == False,
                                     flatten_array(self.window_shape))))

        positions = [(x, y)
                     for x in range(1, width - 1)
                     for y in range(1, height - 1)
                     if self.window_shape[y][x] == 0]

        while free_space > max_steps:
            pos = random.choice(positions)
            self.window_shape[pos[1]][pos[0]] = len(self.food_positions) - 1
            self.food_positions.append(pos)

            free_space -= 1


def play():
    g = Game().reset()

    while True:
        event = g.stdscr.getch()
        direction = (0, 0)
        speed = 0.07

        if event == ord('q'):
            break
        if event == ord('w'):
            direction = (-speed, 0)
        if event == ord('a'):
            direction = (0, -speed)
        if event == ord('s'):
            direction = (speed, 0)
        if event == ord('d'):
            direction = (0, speed)

        g.direction = direction
        gameover, score, high_score, stdscr = g.update_state()

        if gameover:
            show_message("GAME OVER!\nYour Score was: {}\nHighScore:{}"
                         .format(score, high_score), color="red")
            result = input("Do You Want To Play Again?(Y/N)> ")
            if result.lower() == "y":
                play()
            else:
                exit()


play()
