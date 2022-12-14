import Maze
import numpy as np
from PIL import Image, ImageDraw


# created a separate node object for solving so that it would be easier to retrace steps after solving
class Node(object):
    def __init__(self, pos:list, edges:list):
        self.pos = pos
        self.parent = None
        self.edges = edges

    def __eq__(self, other):
        if other == None:
            return False
        elif type(other) == list:
            return self.pos == other
        else:
            return other.pos == self.pos

    def __neq__(self, other):
        if other == None:
            return False
        elif type(other) == list:
            return self.pos != other
        else:
            return other.pos != self.pos

    def __getitem__(self, index: int):
        return self.pos[index]

    def __add__(self, other):
        return [self.pos[0] + other.pos[0], self.pos[1] + other.pos[1]]

    def __sub__(self, other):
        return [self.pos[0] - other.pos[0], self.pos[1] - other.pos[1]]

    def __repr__(self):
        return str(self.pos)

    def __str__(self):
        return str(self.pos)


class Maze_Solver(object):
    def __init__(self, maze:Maze.Maze):
        self.maze = maze

        self.vertices = []
        self.edges = []
        self.path = []

        self.width = self.maze.width
        self.length = self.maze.length

        self.start_pos = None
        self.exit_pos = None

        # create a simple numpy array to map out the corridors and walls
        self.board = self._get_2d()

        # create a node graph where there are only important nodes 
        self._create_graph()

    def _get_2d(self):
        text_maze = self.maze.simple_ascii(save=False)
        zero = np.zeros((len(text_maze[0]), len(text_maze)))

        for y in range(len(text_maze)):
            for x in range(len(text_maze[y])):

                if text_maze[y][x] == '.':
                    zero[y, x] = 1
                elif text_maze[y][x] == 'S':
                    self.start_pos = [x, y]
                    zero[y, x] = 1
                elif text_maze[y][x] == 'E':
                    self.exit_pos = [x, y]
                    zero[y, x] = 1

        return zero

    def _add_directions(self, current:list, dir:list):
        dim = self.board.shape

        if current[0] + dir[0] < 0 or current[0] + dir[0] >= dim[1]:
            return -1

        if current[1] + dir[1] < 0 or current[1] + dir[1] >= dim[0]:
            return -1

        return [current[0] + dir[0], current[1] + dir[1]]

    def _look_around(self, position) -> list:
        if [position[0] - 1, position[1]] in self.vertices:
            return [position[0] - 1, position[1]]

        elif [position[0] + 1, position[1]] in self.vertices:
            return [position[0] + 1, position[1]]

        elif [position[0], position[1] - 1] in self.vertices:
            return [position[0] , position[1] - 1]

        elif [position[0], position[1] + 1] in self.vertices:
            return [position[0], position[1] + 1]

    def _create_graph(self):
        queue = []
        queue.append(self.start_pos)

        visited = []
        previous = None

        while len(queue) > 0:
            current = queue.pop(0)
            visited.append(current)

            # always check if there's any local vertices nearby (it can be None)
            previous = self._look_around(current)

            # filter out local dots by if they're not visited and white
            local_dots = list(map(list, self.neighbors(current[0], current[1])))
            local_dots = list(filter(lambda i: self.board[i[1], i[0]] == 1 and i not in visited, local_dots))

            if len(local_dots) > 1: # choose first local dot and put rest in queue
                for x in local_dots[1:]:
                    if x not in visited and self.board[x[1], x[0]] == 1:
                        queue.append(list(x))

            elif len(local_dots) == 0: # dead end
                if current not in self.vertices: # add dead end to list
                    self.vertices.append(current)

                # create an edge from the current and previous node if exists
                if previous is not None and [previous, current] not in self.edges:
                    self.edges.append([previous, current])

                continue

            dir = [local_dots[0][0]-current[0], local_dots[0][1]-current[1]] # get change in direction

            # get local dots for new position and do same filtering
            next_pos = self._add_directions(current, dir)
            local_dots = list(map(list, self.neighbors(next_pos[0], next_pos[1])))
            local_dots = list(filter(lambda x: self.board[x[1], x[0]] == 1 and x not in visited, local_dots))

            # continue walk until new discovery
            while len(local_dots) in [0, 1] and next_pos not in self.vertices and next_pos not in  visited:
                temp_next = self._add_directions(next_pos, dir)

                if temp_next == -1 or self.board[temp_next[1], temp_next[0]] == 0:
                    break

                visited.append(next_pos)
                next_pos = self._add_directions(next_pos, dir)
                local_dots = list(map(list, self.neighbors(next_pos[0], next_pos[1])))
                local_dots = list(filter(lambda x: self.board[x[1], x[0]] == 1 and x not in visited, local_dots))

            # add new discovery to vertices
            self.vertices.append(list(next_pos))

            # ensure that we have a parent node for edge creation
            if previous == None:
                previous = current
                if previous not in self.vertices:
                    self.vertices.append(previous)

            # create an edge
            if current in self.vertices:
                self.edges.append([current, next_pos])
            else:
                self.edges.append([previous, next_pos])

            # add new position to queue for continued walk
            queue.append(next_pos)

        temp = []
        for x in self.vertices:
            edges = [y for y in self.edges if x == y[0]]
            temp.append(Node(x, edges))

        self.vertices = temp
        for x in self.vertices:
            if x == Node(self.start_pos, []):
                self.start_pos = x
                break

        for x in self.vertices:
            if x == Node(self.exit_pos, []):
                self.exit_pos = x
                break


    def neighbors(self, x:int, y:int):
        """A generator that yields neighboring values.
        
        Args:
            x: x position of the array
            y: y position of the array
        
        Returns:
            x_change: the neighboring node in the x position
            y_change: the neighboring node in the y position
        """

        l, w = self.board.shape

        for yp in range(-1, 2):
            for xp in range(-1, 2):
                if abs(xp) == abs(yp):
                    continue

                if xp + x < 0 or xp + x >= w:
                    continue

                if yp + y < 0 or yp + y >= l:
                    continue

                yield xp + x, yp + y

    def clear(self):
        """Undoes the solving of the maze."""

        for x in self.vertices:
            x.parent = None

    def _show_pairs(self, pair:list, visited:list=None, next_nodes:list=None):
        l, w = self.board.shape

        img = Image.new('RGB', (w, l), color=(0, 0, 0))
        arr = np.array(img)

        for y in range(l):
            for x in range(w):
                if self.board[y, x]:
                    arr[y, x] = (255, 255, 255)

        if visited:
            for x in visited:
                arr[x[1], x[0]] = (0, 0, 255)

        if next_nodes:
            for x in next_nodes:
                arr[x[1], x[0]] = (255, 128, 0)

        for x in pair:
            arr[x[1], x[0]] = (0, 255, 255)

        return Image.fromarray(arr.astype('uint8'), 'RGB')

    def _upscale_image(self, img:Image, scale:int=10) -> Image:
        l, w = self.board.shape

        im = Image.new('RGB', (l*scale, w*scale), (0, 0, 0))
        draw = ImageDraw.Draw(im)
        arr = np.array(img)

        for y in range(l):
            for x in range(w):
                draw.rectangle([(x * scale, y * scale), ((x + 1) * scale, (y + 1) * scale)], fill=tuple(arr[y,x]))

        return im

    def BFS(self):
        queue = [self.start_pos]

        visited = []
        current = None

        while len(queue) > 0:
            if current == self.exit_pos:
                break

            current = queue.pop(0)
            visited.append(current)

            nearby_nodes = [x[1] for x in current.edges]
            nearby_nodes = list(filter(lambda x: x in nearby_nodes, self.vertices))


            if len(nearby_nodes) == 1:
                nearby_nodes[0].parent = current
                queue.append(nearby_nodes[0])

            elif len(nearby_nodes) > 1:
                for x in nearby_nodes:
                    x.parent = current
                    queue.append(x)

        path = []
        while current != self.start_pos:
            path.append(current)
            current = current.parent

        path.append(current)
        path = path[::-1]
        self.path = path

    def DFS(self):
        stack = [self.start_pos]

        visited = []
        current = None

        while len(stack) > 0:
            if current == self.exit_pos:
                break

            current = stack.pop()
            visited.append(current)

            nearby_nodes = [x[1] for x in current.edges]
            nearby_nodes = list(filter(lambda x: x in nearby_nodes, self.vertices))


            if len(nearby_nodes) == 1:
                nearby_nodes[0].parent = current
                stack.append(nearby_nodes[0])

            elif len(nearby_nodes) > 1:
                for x in nearby_nodes:
                    x.parent = current
                    stack.append(x)

        path = []
        while current != self.start_pos:
            path.append(current)
            current = current.parent

        path.append(current)
        path = path[::-1]
        self.path = path

    def walk_animation(self, speed:float=0.75): # not done
        images = []
        visited = []
        for x in self.path:
            visited.append(x)
            images.append(self._show_pairs([x], visited=visited))

        duration = int(len(images) * speed)
        print(duration)

        images = [self._upscale_image(x, 4) for x in images]

        images[0].save('walk.gif',
                       save_all=True, append_images=images[1:], optimize=False, duration=duration, loop=0)

    def show_path(self, upscale:bool=True):
        l, w = self.board.shape

        img = Image.new('RGB', (w, l), color=(0, 0, 0))
        arr = np.array(img)

        for y in range(l):
            for x in range(w):
                if self.board[y, x]:
                    arr[y, x] = (255, 255, 255)

        current = self.exit_pos
        while current != self.start_pos:
            diff = current - current.parent
            index = 0 if diff[0] != 0 else 1

            if index == 0 and diff[index] > 0:
                for x in range(diff[index]):
                    arr[current[1], x+current.parent[0]] = (0, 255, 0)

            elif index == 0 and diff[index] < 0:
                for x in range(abs(diff[index])):
                    arr[current[1], -x+current.parent[0]] = (0, 255, 0)

            elif index == 1 and diff[index] < 0:
                for y in range(abs(diff[index])):
                    arr[-y+current.parent[1], current[0]] = (0, 255, 0)

            else:
                for y in range(diff[index]):
                    arr[y+current.parent[1], current[0]] = (0, 255, 0)

            arr[current[1], current[0]] = (0, 255, 0)
            current = current.parent

        arr[current[1], current[0]] = (0, 255, 0)

        if upscale:
            self._upscale_image(Image.fromarray(arr.astype('uint8'), 'RGB'), 8).save('nodes.png')
        else:
            Image.fromarray(arr.astype('uint8'), 'RGB').save('nodes.png')


def main():
    m = Maze.Maze(length=35, width=35)
    m.read_picture()

    # print("Read the image in")
    # m.iterative_backtrack()
    # m.convert_to_image()

    sol = Maze_Solver(m)
    print("Solving maze")
    sol.BFS()

    print("Saving the maze")
    sol.show_path()
    sol.walk_animation()


if __name__ == '__main__':
    main()
