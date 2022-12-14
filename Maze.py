import random
import numpy as np
from PIL import Image, ImageDraw


class Node(object):
    def __init__(self, x: int, y: int):
        self.x = x
        self.y = y

        # N S E W
        self.walls = [1, 1, 1, 1]

    def clear(self):
        """
        Resets the wall for the node
        """
        self.walls = [1, 1, 1, 1]

    def __repr__(self):
        return str(self.__dict__)

    def __str__(self):
        return str(self.__dict__)

    def __add__(self, other):
        if type(other) == Node:
            return [self.x + other.x, self.y + other.y]
        elif type(other) == list and len(other) == 2:
            return [self.x + other[0], self.y + other[1]]

    def __sub__(self, other):
        if type(other) == Node:
            return [self.x - other.x, self.y - other.y]
        elif type(other) == list and len(other) == 2:
            return [self.x - other[0], self.y - other[1]]


class Maze(object):
    """A Maze object that holds a 2d array of nodes. Can generate a maze with 2 different methods.

    Args:
        length: the number of nodes long
        width: the number of nodes wide
    """

    def __init__(self, length: int = 5, width: int = 5):

        self.length = length
        self.width = width

        # create a 2d array of nodes
        self.grid = [[Node(x, y) for x in range(self.width)] for y in range(self.length)]
        self.start_node = Node(0, 0)

    def change_wall(self, x: int, y: int, wall: int):
        if wall == 0:
            
            # Ensures if wall is edge of map or not
            if y == 0:
                self.grid[y][x].walls[0] = int(not self.grid[y][x].walls[0])
            else:
                self.grid[y][x].walls[0] = int(not self.grid[y][x].walls[0])
                self.grid[y - 1][x].walls[1] = int(not self.grid[y - 1][x].walls[1])

        elif wall == 1:

            # Ensures if wall is edge of map or not
            if y == self.length - 1:
                self.grid[y][x].walls[1] = int(not self.grid[y][x].walls[1])
            else:
                self.grid[y][x].walls[1] = int(not self.grid[y][x].walls[1])
                self.grid[y + 1][x].walls[0] = int(not self.grid[y + 1][x].walls[0])

        elif wall == 2:
            
            # Ensures if wall is edge of map or not
            if x == self.width - 1:
                self.grid[y][x].walls[2] = int(not self.grid[y][x].walls[2])
            else:
                self.grid[y][x].walls[2] = int(not self.grid[y][x].walls[2])
                self.grid[y][x + 1].walls[3] = int(not self.grid[y][x + 1].walls[3])

        elif wall == 3:
            
            # Ensures if wall is edge of map or not
            if x == 0:
                self.grid[y][x].walls[3] = int(not self.grid[y][x].walls[3])
            else:
                self.grid[y][x].walls[3] = int(not self.grid[y][x].walls[3])
                self.grid[y][x - 1].walls[2] = int(not self.grid[y][x - 1].walls[2])

    def neighbors(self, x: int, y: int, diagonal: bool = False):
        """A generator that yields neighboring values.
        
        Args:
            x: x position of the array
            y: y position of the array
            diagonal: boolean if diagonal neighbors are allowed or not
        
        Returns:
            neighboring_node: a node that is near the current node
        """

        for yp in range(-1, 2):
            for xp in range(-1, 2):
                if xp == 0 and yp == 0:
                    continue

                if not diagonal and [abs(xp), abs(yp)] == [1, 1]:
                    continue

                if xp + x < 0 or xp + x >= self.width:
                    continue

                if yp + y < 0 or yp + y >= self.length:
                    continue

                yield self.grid[yp + y][xp + x]

    def _wall_exists(self, first: Node, second: Node, wall: int) -> bool:
        """
        Private function that checks if there is a wall between two nodes

        Args:
            first: Node to compare
            second: Node to compare
            wall: wall index to check between the nodes
        
        Returns:
            bool: if there is a wall exists or doesn't between the two nodes
        """

        # North and East walls always have their neighbor +1 from their direction
        if wall in [0, 2]:
            return first.walls[wall] == second.walls[wall + 1]

        # South and West walls always have their neighbor -1 from their direction
        elif wall in [1, 3]:
            return first.walls[wall] == second.walls[wall - 1]

    def _convert_pos(self, position):
        """
        Get the directional difference between two nodes and 
        Args:
            position: a list with the difference in position of two nodes
        
        Returns:
            index: wall index of where the wall should be removed
        """
        directions = {
            "N": [0, -1],
            "S": [0, 1],
            "E": [1, 0],
            "W": [-1, 0]
        }

        for x, y in directions.items():
            if position == y:
                return list(directions.keys()).index(x)

    def clear(self):
        """
        Resets the maze by resetting the walls for each node
        """

        for y in range(self.length):
            for x in range(self.width):
                self.grid[y][x].clear()

    def display_maze(self):
        """
        Print out maze to terminal
        Args:
            None
        
        Returns:
            None
        """

        row = [' ']
        for x in range(self.width):
            if self.grid[0][x].walls[0]:
                row.append('_')
            else:
                row.append(' ')

            row.append(' ')

        print("".join(row))

        for y in range(self.length):
            row = []
            for x in range(self.width):
                current = self.grid[y][x]

                if x == 0:
                    if current.walls[3] == 1:
                        row.append('|')
                    else:
                        row.append(' ')

                if current.walls[1] == 1:
                    row.append('_')
                else:
                    row.append(' ')

                if current.walls[2] == 1 and x + 1 < self.width and self.grid[y][x + 1].walls[3] == 1:
                    row.append('|')

                elif current.x == self.width - 1 and current.walls[2] == 1:
                    row.append('|')

                else:
                    row.append(' ')

            print("".join(row))

    def convert_to_image(self, name:str='maze.png', save:bool=True) -> Image:
        """
        Converts maze into an image. When saving, two images are generated 
        where one is 1:1 to solve and another for actually viewing.

        Args:
            name: name for file output
            save: boolean for saving to a file
        
        Returns:
            image: Returns the Pillow image for possible uses
        """
        # setup a blank, white image
        l, w = (self.length * 2) + 1, (self.width * 2) + 1
        img = Image.new('RGB', (w, l), color=(255, 255, 255))
        arr = np.array(img)

        # add a black border around the maze
        arr[0, :] = (0, 0, 0)
        arr[:, 0] = (0, 0, 0)
        arr[l - 1, :] = (0, 0, 0)
        arr[:, w - 1] = (0, 0, 0)

        for y in range(self.length):
            for x in range(self.width):

                # create an array where all of the node positions of the image in the x and y axis are made
                translate_y = [i + 1 for i in list(range(0, l - 1, 2))]
                translate_x = [i + 1 for i in list(range(0, w - 1, 2))]
                current = self.grid[y][x]

                # if an east wall exists then fill in the nearby pixels with black
                if current.walls[2]:
                    arr[translate_y[y], translate_x[x] + 1] = (0, 0, 0)
                    arr[translate_y[y] + 1, translate_x[x] + 1] = (0, 0, 0)
                    arr[translate_y[y] - 1, translate_x[x] + 1] = (0, 0, 0)

                # if a south wall exists then fill in the nearby pixels with black
                if current.walls[1]:
                    arr[translate_y[y] + 1, translate_x[x] + 1] = (0, 0, 0)
                    arr[translate_y[y] + 1, translate_x[x] - 1] = (0, 0, 0)
                    arr[translate_y[y] + 1, translate_x[x]] = (0, 0, 0)

        # places a green and red color for the start and end
        arr[0, 1] = (0, 255, 0)
        arr[l - 1, w - 2] = (255, 0, 0)

        # convert to image for potential uses
        new_img = Image.fromarray(arr.astype('uint8'), 'RGB')

        if save:
            new_img.save(name)
            upscale = self.upscale_image(new_img)
            upscale.save("upscaled.png")

        return new_img

    def upscale_image(self, img:Image, scale:int=10) -> Image:
        l, w = (self.length * 2) + 1, (self.width * 2) + 1

        im = Image.new('RGB', (l*scale, w*scale), (0, 0, 0))
        draw = ImageDraw.Draw(im)
        arr = np.array(img)

        for y in range(l):
            for x in range(w):
                draw.rectangle([(x * scale, y * scale), ((x + 1) * scale, (y + 1) * scale)], fill=tuple(arr[y,x]))

        return im

    def simple_ascii(self, name:str="maze.txt", save:bool=True):
        """Generates maze as a string array.

        Args:
            name: name of the text file for the maze
            save: boolean to save the maze as a text file

        Returns:
            arr: string array
        """

        l, w = (self.length * 2) + 1, (self.width * 2) + 1

        arr = [['.' for _ in range(w)] for _ in range(l)]

        for x in range(l):
            arr[0][x] = '#'
            arr[l-1][x] = '#'

        for x in range(w):
            arr[x][0] = '#'
            arr[x][w - 1] = '#'

        for y in range(self.length):
            for x in range(self.width):
                translate_y = [i + 1 for i in list(range(0, l - 1, 2))]
                translate_x = [i + 1 for i in list(range(0, w - 1, 2))]
                current = self.grid[y][x]

                if current.walls[2]:
                    arr[translate_y[y]][translate_x[x] + 1] = '#'
                    arr[translate_y[y] + 1][translate_x[x] + 1] = '#'
                    arr[translate_y[y] - 1][translate_x[x] + 1] = '#'

                if current.walls[1]:
                    arr[translate_y[y] + 1][translate_x[x] + 1] = '#'
                    arr[translate_y[y] + 1][translate_x[x] - 1] = '#'
                    arr[translate_y[y] + 1][translate_x[x]] = '#'

        arr[0][1] = 'S'
        arr[l - 1][w - 2] = 'E'

        if save:
            with open(f"{name}", "w") as fh:
                for x in arr:
                    fh.write(f"{' '.join(x)}\n")

        return arr

    def read_picture(self, name:str='maze.png'):
        """
        Reads in an image of a maze. Maze must be 1:1 in terms of pixel to node

        Args:  
            Name: name of the input image
        
        Returns: 
            None
        """

        img = Image.open(name)
        arr = np.array(img)

        self.width = (img.width - 1) // 2
        self.length = (img.height - 1) // 2

        self.grid = [[Node(x, y) for x in range(self.width)] for y in range(self.length)]

        for y in range(1, img.height, 2):
            for x in range(1, img.width, 2):
                translated_pos = self._translate_pos(x, y)
                current = self.grid[translated_pos[1]][translated_pos[0]]

                if y+1 <= img.height-1:
                    if all([i==255 for i in arr[y+1, x]]):
                        self.grid[current.y+1][current.x].walls[0] = 0
                        current.walls[1] = 0

                if x+1 <= img.width-1:
                    if all([i==255 for i in arr[y, x+1]]):
                        self.grid[current.y][current.x+1].walls[3] = 0
                        current.walls[2] = 0

    def _translate_pos(self, x:int, y:int):
        new_pos = [0, 0]

        if x == 1:
            new_pos[0] = 0
        else:
            new_pos[0] = x//2

        if y == 1:
            new_pos[1] = 0
        else:
            new_pos[1] = y//2

        return new_pos

    def iterative_backtrack(self):
        """Uses backtracking to explore all nodes randomly to generate maze."""

        # start stack with the starting node and an empty array of visited positions
        stack = [self.start_node]
        visited = []

        while len(stack) > 0:
            # remove node from stack and add it to visited array
            current = stack.pop()
            visited.append((current.x, current.y))

            # get available neighbors and randomly shuffle them
            available_nodes = [x for x in self.neighbors(current.x, current.y) if not (x.x, x.y) in visited]
            random.shuffle(available_nodes)

            # checks if there are at least 1 available node to visit
            if len(available_nodes) > 0:
                # add first node to the stack and get it's direction from current node
                stack.append(current)
                next_cell = available_nodes.pop()
                position = next_cell - current

                wall = self._convert_pos(position)
                self.change_wall(current.x, current.y, wall)

                stack.append(next_cell)

    def Aldous_Broder(self):
        current = self.start_node
        visited = []

        while not all([(x, y) in visited for x in range(self.width) for y in range(self.length)]):
            available_nodes = [i for i in self.neighbors(current.x, current.y)]
            next_node = random.choice(available_nodes)

            if not (next_node.x, next_node.y) in visited:
                position = next_node - current
                wall = self._convert_pos(position)

                self.change_wall(current.x, current.y, wall)

            visited.append((current.x, current.y))
            current = next_node


def main():
    m = Maze(length=25, width=25)
    m.Aldous_Broder()

    m.convert_to_image(save=True)


if __name__ == '__main__':
    main()
