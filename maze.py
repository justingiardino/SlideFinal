#create a maze solver first following bookmark then try and do the puzzle one
import time
import platform

#enable ANSI escape codes on windows
if platform.system() == 'Windows':
    import colorama
    colorama.init()

import breadth_first_search
#add display of vertices and then show puzzle solving using vertices


class Maze(object):

    def __init__(self):

        self.debug_mode = 0
        while self.debug_mode != 1 and self.debug_mode != 2:
            self.debug_mode = int(input("Do you want debug mode on?\n1) Yes\n2) No\n>"))

        if platform.system() == 'Windows':
            self.color_dict = {'0':'\033[0m', '1':'\033[0;31m','2':'\033[0;32m','3':'\033[0;37m','4':'\033[0;36m','5':'\033[1;33m','6':'\033[0;35m'}#,'f':'\033[0;37m','g':'\033[1;34m','h':'\033[1;32m','i':'\033[1;36m','j':'\033[1;35m'}
        else:
            self.color_dict = {'0':'\033[0m', '1':'\033[0;31m','2':'\033[0;34m','3':'\033[0;37m','4':'\033[0;36m','5':'\033[1;33m','6':'\033[0;35m'}#,'f':'\033[0;37m','g':'\033[1;34m','h':'\033[1;32m','i':'\033[1;36m','j':'\033[1;35m'}

        self.prev_dir = 'None'#keep track of last direction
        self.vertex_dict = {0:{'adj_dir':{}}} # format 'Label' : {vertex1:direction1, vertex2:direction2} - Old 'Vertex Label' : set([adjacent vertex list]) # 1 : [2,3],
        self.next_vertex_label = 0 #used to increment vertex label count
        self.current_vertex_label = 0 #keep track of which path you are on
        self.final_graph = {}
        self.main_maze = []
        self.vertex_maze = []
        self.exit_in_path = False
        self.exit_path_coords = [] #{'v':0, 'h':0}#, 'icon': ' '} #board should never be at 0,0 and I need initial values
        self.exit_path_icons = {}
        self.direction_dict =  {'Up':{'icon':'^', 'v_offset': -1, 'h_offset': 0},
                                'Down':{'icon':'v', 'v_offset': 1, 'h_offset': 0},
                                'Left':{'icon':'<', 'v_offset': 0, 'h_offset': -1},
                                'Right':{'icon':'>', 'v_offset': 0, 'h_offset': 1}}

        self.load_maze()
        self.find_start()

    def load_maze(self):
        # with open('Mazes/maze_layout.txt', 'r') as maze_read:
        # with open('Mazes/maze_layout_no_alt_path.txt', 'r') as maze_read:
        # with open('Mazes/maze_layout_complex.txt', 'r') as maze_read:
        with open('Mazes/maze_layout_complex_multiple_exit.txt', 'r') as maze_read:
        # with open('Mazes/maze_layout_more_complex.txt', 'r') as maze_read:
        # with open('Mazes/maze_layout_more_complex2.txt', 'r') as maze_read:
        # with open('Mazes/maze_layout_another_complex.txt', 'r') as maze_read:
        # with open('Mazes/maze_layout_last_complex.txt', 'r') as maze_read:
            maze_in = maze_read.read().splitlines()
        #get board dimensions
        self.v_size = len(maze_in)
        self.h_size = len(maze_in[0])

        for line in maze_in:
            self.main_maze.append(list(line))
            self.vertex_maze.append(list(line))
        self.build_blank_found()


    def build_blank_found(self):
        self.found_dict = {}
        for v in range(self.v_size):
            self.found_dict[v] = {}
            for h in range(self.h_size):
                self.found_dict[v][h] = {'found':[]}
        #print("Build Test:{}".format(self.found_dict[0][0]))


    def find_start(self):
        for v in range(self.v_size):
            for h in range(self.h_size):
                if self.main_maze[v][h] == 'S':
                    self.start_v = v
                    self.start_h = h
        #update vertex_dict
        self.vertex_dict[0]['coord_v'] = self.start_v
        self.vertex_dict[0]['coord_h'] = self.start_h

    def print_maze(self):
        for v in range(self.v_size):
            for h in range(self.h_size):
                print(self.main_maze[v][h],end="")
            print("")


    #adds vertex labels to vertex maze for printing
    def build_vertex_graph(self):
        for vertex in self.vertex_dict.keys():
            v = self.vertex_dict[vertex]['coord_v']
            h = self.vertex_dict[vertex]['coord_h']
            if self.vertex_maze[v][h] != 'S':
                self.vertex_maze[v][h] = vertex


    #going to change color of value if the number is greater than 10
    def print_vertex_maze(self):
        str_list = ['#', 'S', ' ', 'E','v','^', '<','>']
        for v in range(self.v_size):
            for h in range(self.h_size):
                curr_val = self.vertex_maze[v][h]
                if curr_val in str_list:
                    print(curr_val,end="")
                else:
                    #number less than 10, print it normally
                    print_info = int(curr_val) / 10
                    #print("Print info: {}".format(print_info))
                    color, vert_number = str(print_info).split('.')
                    print("{}{}\033[0m".format(self.color_dict[color], vert_number),end="")
                    #else number is greater
            print("")

    # #main game function
    def game_play(self):
        start = time.time()
        print("Calling new solve maze")
        self.solve_maze(self.start_v, self.start_h)
        #self.solve_maze_old(self.start_v, self.start_h)
        #self.print_maze()
        end = time.time()
        ms_time = round(((end-start) * 1000),4)
        print("Game over, maze completed!\nTime for completion: {} ms".format(ms_time))
        print("Printing vertex maze for reference")
        self.print_vertex_maze()
        #self.search_extra_vertex()

        #print("Current vertex_dict: {}".format(self.vertex_dict))

        self.solve_path()


    #this is the vertex section to find the best path
    def solve_path(self):

        self.build_final_graph()
        print("\n{}".format(self.final_graph))
        breadth_first_search.print_graph(self.final_graph)
        self.solution_list = list(breadth_first_search.dfs_paths(self.final_graph, 0, 'E'))#get rid of unecessary double list
        print("All solutions: {}".format(self.solution_list))
        print("Shortest solution: {}".format(self.solution_list[0]))
        # print("Tens value and color it will be\n" + "-"*25)
        # for temp_color in self.color_dict.keys():
        #     print(" "*5 + "{}{}0\'s\033[0m".format(self.color_dict[temp_color], temp_color))
        # print("Printing vertex maze")
        self.print_vertex_maze()
        print("End of solve_path, calling update vertex maze")
        print("Exit path coords: {}\nExit path icons: {}".format(self.exit_path_coords,self.exit_path_icons))
        self.update_vertex_maze(self.solution_list[0])

    #function is used
    #check to see what we need to do with vertex_dict
    def check_vertex(self, v_search, h_search):
        print("Next vertex label: {}".format(self.next_vertex_label))
        print("Current vertex label: {}".format(self.current_vertex_label))

        #check to see if vertex is already at this location
        for vertex in self.vertex_dict.keys():
            if self.vertex_dict[vertex]['coord_v'] == v_search and self.vertex_dict[vertex]['coord_h'] == h_search:
                print("This vertex ({}) already exists\nResetting current vertex label.\nLeaving function.".format(vertex))
                self.current_vertex_label = vertex
                return

        print("Leaving for loop, didn't find an existing vertex here. Need to add a new one")

        #Adding new vertex to dict
        self.next_vertex_label += 1
        #Adding new vertex to adj_dir of last vertex
        #Redoing logic on adj_dir
        # self.vertex_dict[self.current_vertex_label]['adj_dir'].append(self.next_vertex_label)
        self.vertex_dict[self.current_vertex_label]['adj_dir'][self.next_vertex_label] = self.prev_dir
        self.current_vertex_label = self.next_vertex_label
        self.vertex_dict[self.next_vertex_label] = {'adj_dir': {}, 'coord_v': v_search, 'coord_h': h_search}
        #this is where I want to display the vertex on the graph
        if self.vertex_maze[v_search][h_search] == ' ':
            self.vertex_maze[v_search][h_search] = self.current_vertex_label

    #used for printing
    #needs to be modified
    #takes current solution list as an input since it could be a different solution that I want to display
    def update_vertex_maze(self, curr_solution_list):
        input("Starting solution\n>")
        #self.direction_dict =  {'Up':{'icon':'^', 'v_offset': -1, 'h_offset': 0},
        # v_off_dict = {'Right': 0, 'Left': 0, 'Up': -1, 'Down': 1}
        # h_off_dict = {'Right': 1, 'Left': -1, 'Up': 0, 'Down': 0}
        # dir_icon = {'Right': '>', 'Left': '<', 'Up': '^', 'Down': 'v'}
        #print("Current vertex dict: \n{}".format(self.vertex_dict))
        print("Length of solution list: {}".format(len(curr_solution_list)))
        for index, vertex in enumerate(curr_solution_list):

            # if index == len(curr_solution_list) - 1:
            #     print("Made it to last vertex before exit.")
            #     print("Exit is at v: {}, h: {} in direction: {}".format(self.vertex_dict['E']['coord_v'], self.vertex_dict['E']['coord_h'], self.final_e_dir))
            #     final_v = self.e_coords['v']
            #     final_h = self.e_coords['h']
            #     move_dir = self.final_e_dir
            # else:
            move_dir = self.vertex_dict[vertex]['adj_dir'][curr_solution_list[index + 1]]
            next_vertex = curr_solution_list[index + 1]
            print("Index: {}, Vertex: {}, Next Vertex: {}, Direction: {}".format(index, vertex, next_vertex, move_dir))
            final_v = self.vertex_dict[next_vertex]['coord_v']
            final_h = self.vertex_dict[next_vertex]['coord_h']

            curr_v = self.vertex_dict[vertex]['coord_v']
            curr_h = self.vertex_dict[vertex]['coord_h']
            curr_icon = self.direction_dict[move_dir]['icon']
            #curr_icon = dir_icon[move_dir]
            # v_offset = v_off_dict[move_dir]
            v_offset = self.direction_dict[move_dir]['v_offset']
            # h_offset = h_off_dict[move_dir]
            h_offset = self.direction_dict[move_dir]['h_offset']
            print("curr_v: {}, curr_h: {}".format(curr_v, curr_h))
            print("Next v: {}, next h: {}".format(final_v, final_h))

            new_vertex = False
            while new_vertex == False:
                if self.vertex_maze[curr_v][curr_h] != 'S':
                    self.vertex_maze[curr_v][curr_h] = curr_icon
                curr_v += v_offset
                curr_h += h_offset
                if curr_v == final_v and curr_h == final_h:
                    print("Reached new vertex")
                    new_vertex = True

            self.print_vertex_maze()
            if next_vertex == 'E':
                print("Found exit, returning!")
                return
            else:
                input("Next move?\n>")


    #this is the graph that I pass to breadth first search
    def build_final_graph(self):
        for vertex in self.vertex_dict.keys():
            #self.build_adj_dir(vertex)
            #want to only take the vertices here, not the direction moving - only want the keys
            print("Current adjacent directions for vertex: {}: {}".format(vertex, self.vertex_dict[vertex]['adj_dir']))
            self.final_graph[vertex] = set(self.vertex_dict[vertex]['adj_dir'].keys())
        #print(self.final_graph)


    #function is used
    #new method of solving maze
    #find all directions that are open and then loop through each of those directions
    #return when no more directions are found
    def solve_maze(self, v_search, h_search):
        #don't want to overwrite start
        if self.main_maze[v_search][h_search] != 'S':
            self.main_maze[v_search][h_search] = 'O'

        self.print_maze()
        #print("Current vertex list: {}\nCurrently at v: {}, h: {}\nCurrent vertex label: {}".format(self.vertex_dict, v_search, h_search, self.current_vertex_label))

        print("Currently at v: {}, h: {}\nCurrent Vertex Dict: {}".format(v_search, h_search, self.vertex_dict))
        if self.debug_mode == 1:
            input("Next Step?\n>")
        else:
            print("Next Step?\n>")

        #Check down
        if v_search < self.v_size-2:
            if self.main_maze[v_search+1][h_search] == ' ' or  self.main_maze[v_search+1][h_search] == 'E':
                print("Move found below")
                self.found_dict[v_search][h_search]['found'].append('Down')

        #check up
        if v_search > 1:
            if self.main_maze[v_search-1][h_search] == ' ' or  self.main_maze[v_search-1][h_search] == 'E':
                print("Move found above")
                self.found_dict[v_search][h_search]['found'].append('Up')

        #check right
        if h_search < self.h_size-2:
            if self.main_maze[v_search][h_search+1] == ' ' or  self.main_maze[v_search][h_search+1] == 'E':
                print("Move found to the right")
                self.found_dict[v_search][h_search]['found'].append('Right')

        #check left
        if h_search > 1:
            if self.main_maze[v_search][h_search-1] == ' '  or  self.main_maze[v_search][h_search-1] == 'E':
                print("Move found to the left")
                self.found_dict[v_search][h_search]['found'].append('Left')

        if len(self.found_dict[v_search][h_search]['found']) > 1:
            print("Multiple directions found, need a vertex")
            self.check_vertex(v_search, h_search)

        #continue through this loop until there are no more direction to check for a grid position
        while self.found_dict[v_search][h_search]['found']:

            #if you make it back to the top of this loop meaning there is another direction
            #and if you have already found an exit path
            #want to branch off of the existing exit path and try new direction
            #not sure what would happen if there were multiple exit paths
            if self.exit_in_path == True:
                if self.debug_mode == 1:
                    input("Had already found exit, but there is another direction to try.\n>")
                else:
                    print("Had already found exit, but there is another direction to try.\n>")
                self.current_vertex_label = self.vertex_maze[v_search][h_search]
                self.exit_in_path = False
                self.exit_path_coords.append({'v': v_search, 'h': h_search})#['v'] = v_search
                #self.exit_path_coords['h'] = h_search
                #create dictionary for icon at that location
                self.exit_path_icons[v_search] = {}
                self.exit_path_icons[v_search][h_search] = self.main_maze[v_search][h_search]
                #self.exit_path_coords['icon'] =

            if self.debug_mode == 1:
                input("Move(s) found at v: {}, h: {} are:\n{}\n>".format(v_search, h_search, self.found_dict[v_search][h_search]['found']))
            else:
                print("Move(s) found at v: {}, h: {} are:\n{}".format(v_search, h_search, self.found_dict[v_search][h_search]['found']))

            #start move process
            move_dir = self.found_dict[v_search][h_search]['found'].pop()

            #change icon to direction if not the start piece, as long as piece isn't S
            if self.main_maze[v_search][h_search] != 'S':
                self.main_maze[v_search][h_search] = self.direction_dict[move_dir]['icon']

            #else if is the S position and the prev dir hasn't been set yet, need to set it
            elif self.prev_dir == 'None':
                print("Currently at the start, but have not set a previous direction, setting now")
                self.prev_dir = move_dir


            v_off = self.direction_dict[move_dir]['v_offset']
            h_off = self.direction_dict[move_dir]['h_offset']

            #this is where I want to check for a new verex
            if move_dir != self.prev_dir:
                print("Changing direction, checking to see if a new vertex is needed")

                self.check_vertex(v_search, h_search) #issue here when there are multiple directions but the first one it tries is the same direction
                self.prev_dir = move_dir


            #if the next move would be the exit, return instead of calling recursion again
            if self.main_maze[v_search + v_off][h_search + h_off] == 'E':
                self.print_maze()
                self.exit_in_path = True
                if self.debug_mode == 1:
                    input("Found exit, Going back to previous level in recursion\n>")
                else:
                    print("Found exit, Going back to previous level in recursion\n>")
                #add to vertex list if it doesn't exist
                if 'E' not in self.vertex_dict.keys():
                    self.vertex_dict['E'] = {'adj_dir': {}, 'coord_v': v_search+v_off, 'coord_h': h_search+h_off}

                #add to last vertex's adj_dir
                self.vertex_dict[self.current_vertex_label]['adj_dir']['E'] = move_dir

                return

            #add vertex label to all grid positions for verification


            # self.print_vertex_maze()
            # if self.debug_mode == 1:
            #     input("Current vertex maze\n>")
            # else:
            #     print("Current vertex maze")
            #call recursive function and continue moving in that direction
            self.solve_maze(v_search + v_off, h_search + h_off)

        #leaving while loop for directions found
        if self.debug_mode == 1:
            input("No more moves found at v: {}, h: {}\nExit in path: {}, Exit path coords: {}\n>".format(v_search, h_search,self.exit_in_path, self.exit_path_coords))
        else:
           print("No more moves found at v: {}, h: {}".format(v_search, h_search))

        #when you are looping back to check all available paths after finding the exit
        #this will catch where you broke off from the main path
        if self.exit_in_path == False and {'v':v_search, 'h':h_search} in self.exit_path_coords:#v_search == self.exit_path_coords['v'] and self.exit_path_coords['h'] == h_search:
            print("Exit in path was false and you are back to where you left the main path. Restting icon")
            self.main_maze[v_search][h_search] = self.exit_path_icons[v_search][h_search]
            self.exit_in_path = True


        #bad location, mark as do not check
        if self.main_maze[v_search][h_search] != 'S' and self.exit_in_path == False:
            self.main_maze[v_search][h_search] = 'X'

        self.print_maze()




if __name__ == '__main__':
    m = Maze()
    #m.print_maze()
    m.game_play()
