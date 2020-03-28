import copy
import time
import breadth_first_search
import sys
import os
#ran into recursion error
sys.setrecursionlimit(10000)

class Board(object):

    def __init__(self):

        self.v_size = 0 #board height
        self.h_size = 0 #board width
        self.blank_board =[] #used in print_board, initialize after getting board size
        self.piece_list = [] #keep track of all pieces
        self.piece_objects = {} # keep track of piece attributes at each vertex in format of {vertex1:{piece1:{start_v:v1-1, start_h:h1-1,length:l1, direction,d1},piece2:{start_v:v1-2, start_h:h1-2,length:l2, direction,d2}}, vertex2:{piece1:{start_v:v2-1, start_h:h2-1,length:l1, direction,d1},piece2:{start_v:v2-2, start_h:h2-2,length:l2, direction,d2}}
        self.board_objects = {} # keep track of what board looks like at each vertex
        self.vertex_dict = {} # keep track of vertex adjacencies
        self.end_vertices = [] # keep track of vertices that result in the game being won
        self.final_graph = {} # dictionary of sets to be passed to breadth first seach
        self.final_solutions = [] # shortest solution list, may just be one item
        print("Welcome to the newest slide puzzle solver!\n")
        self.debug_mode = int(input("Would you like to turn on debug mode?\n1) Yes\n2) No\n>"))
        self.load_board()
        print("\n\n" + "*"*20 + "\nBoard loaded, starting solver")
        self.vertex_dict[0] = []
        start = time.time()
        self.solve_puzzle(0)
        end = time.time()
        build_graph_time = round((end - start), 4)
        input(f"Finished analyzing all moves!\nTime elapsed: {build_graph_time} seconds\nDetermining best path..\n>")
        #changed to bfs
        self.find_best_path_bfs()
        self.print_final_solutions()
        print("""
    _______ _                   _____ _        _
   |__   __(_)                 / ____| |      | |        _
      | |   _ _ __ ___   ___  | (___ | |_ __ _| |_ ___  (_)
      | |  | | '_ ` _ \ / _ \  \___ \| __/ _` | __/ __|
      | |  | | | | | | |  __/  ____) | || (_| | |_\__ \  _
      |_|  |_|_| |_| |_|\___| |_____/ \__\__,_|\__|___/ (_)
        """)
        print(f"\n\t\tPre-processing: {build_graph_time} seconds\n\t\tPath finding: {self.bfs_time} seconds")

    #add border print later
    def print_board_simple(self, current_board):
        for v in range(self.v_size):
            for h in range(self.h_size):
                print(current_board[v][h],end='')
            print("")

    #debugging only
    def print_piece_stats(self, current_vertex):
        for piece in self.piece_objects[current_vertex].keys():
            print(f"Piece: {piece}\nStart_v: {self.piece_objects[current_vertex][piece]['start_v']}\nStart_h: {self.piece_objects[current_vertex][piece]['start_h']}\nLength: {self.piece_objects[current_vertex][piece]['length']}\nDirection: {self.piece_objects[current_vertex][piece]['direction']}\n")

    #initialize board display with pieces
    def build_print_board(self, current_vertex):
        print("In print board")
        #creating temporary show board
        show_board = [['.' for x in range(self.h_size)] for y in range(self.v_size)]
        #build show board based on current vertex
        self.print_piece_stats(current_vertex)
        for piece in self.piece_objects[current_vertex].keys():
            print(f"Piece: {piece}")
            #print horiztonal piece
            if self.piece_objects[current_vertex][piece]['direction'] == 'h':
                for h_off in range(self.piece_objects[current_vertex][piece]['length']):
                    show_board[self.piece_objects[current_vertex][piece]['start_v']][self.piece_objects[current_vertex][piece]['start_h']+h_off] = piece

            #print vertical piece
            elif self.piece_objects[current_vertex][piece]['direction'] == 'v':
                for v_off in range(self.piece_objects[current_vertex][piece]['length']):
                    show_board[self.piece_objects[current_vertex][piece]['start_v']+v_off][self.piece_objects[current_vertex][piece]['start_h']] = piece
        print(show_board)
        self.board_objects[current_vertex] = show_board
        # self.print_board_simple(show_board)


    def load_board(self):
        puzzle_choice = 0
        puzzle_vals = [1,2,3,4,5,6]
        while puzzle_choice not in puzzle_vals:
            puzzle_choice = int(input("Which puzzle?\n1)Small\n2)Regular1\n3)Regular2\n4)Intermediate1\n5)Expert1\n6)Expert2\n>"))
        if puzzle_choice == 1:
            with open('Sliders/puzzle_layout_small.txt', 'r') as puzzle_read:
                puzzle_in = puzzle_read.read().splitlines()
        elif puzzle_choice == 2:
            with open('Sliders/puzzle_layout.txt', 'r') as puzzle_read:
                puzzle_in = puzzle_read.read().splitlines()
        elif puzzle_choice == 3:
            with open('Sliders/puzzle_layout2.txt', 'r') as puzzle_read:
                puzzle_in = puzzle_read.read().splitlines()
        elif puzzle_choice == 4:
            with open('Sliders/puzzle_layout3.txt', 'r') as puzzle_read:
                puzzle_in = puzzle_read.read().splitlines()
        elif puzzle_choice == 5:
            with open('Sliders/puzzle_layout4.txt', 'r') as puzzle_read:
                puzzle_in = puzzle_read.read().splitlines()
        elif puzzle_choice == 6:
            with open('Sliders/puzzle_layout5.txt', 'r') as puzzle_read:
                puzzle_in = puzzle_read.read().splitlines()

        self.v_size = len(puzzle_in)
        self.h_size = len(puzzle_in[0])
        self.blank_board = [['.' for x in range(self.h_size)] for y in range(self.v_size)]
        self.print_board_simple(puzzle_in)

        print("Building board..")
        invalid_piece_list = ['#','.','_']
        #build board
        self.piece_objects[0]= {}
        for v in range(self.v_size):
            for h in range(self.h_size):
                #if finding for the first time, create dictionary value
                current_piece = puzzle_in[v][h]
                #only want to find letters
                if(current_piece not in invalid_piece_list):
                    #initialize piece stats if it hasn't been added yet
                    if(current_piece not in self.piece_objects[0].keys()):
                        self.piece_objects[0][current_piece] = {'start_v':v, 'start_h':h,'length':1}
                        ##check direction, won't be above or to the left and check boundaries, make sure you aren't in the last row or column
                        if(v < self.v_size-1):
                            if(puzzle_in[v+1][h] == current_piece):
                                #update direction as v - vertical
                                self.piece_objects[0][current_piece]['direction'] = 'v'
                        if(h < self.h_size-1):
                            if(puzzle_in[v][h+1] == current_piece):
                                #update direction as h - horizontal
                                self.piece_objects[0][current_piece]['direction'] = 'h'
                    #increment length if letter has already been added
                    else:
                        self.piece_objects[0][current_piece]['length']+=1
        self.build_print_board(0)

    #main recursive function
    def solve_puzzle(self, current_vertex):
        #check movability of each piece
        for piece in self.piece_objects[current_vertex].keys():
            print(f"Current vertex: {current_vertex} Current piece: {piece}\nCurrent board:")
            self.print_board_simple(self.board_objects[current_vertex])
            if self.debug_mode == 1:
                print(f"Current vertex_dict: {self.vertex_dict}")
            temp_board = copy.deepcopy(self.board_objects[current_vertex])
            if self.debug_mode == 1:
                input("Continue to check this piece\n>")
            if self.piece_objects[current_vertex][piece]['direction'] == 'h':
                print(f"piece: {piece} Direction: Horizontal")
                #check move left
                if self.piece_objects[current_vertex][piece]['start_h'] == 0:
                    print("Can't move left, boundary issue")
                elif temp_board[self.piece_objects[current_vertex][piece]['start_v']][self.piece_objects[current_vertex][piece]['start_h']-1] != '.':
                    print("Can't move left, other piece in the way")
                else:
                    print("Temporarily moving left")
                    temp_board[self.piece_objects[current_vertex][piece]['start_v']][self.piece_objects[current_vertex][piece]['start_h']-1] = piece
                    temp_board[self.piece_objects[current_vertex][piece]['start_v']][self.piece_objects[current_vertex][piece]['start_h'] + self.piece_objects[current_vertex][piece]['length']-1] = '.'
                    # print(temp_board)
                    self.print_board_simple(temp_board)

                    #if haven't already found this board, move to new vertex
                    if temp_board not in self.board_objects.values():
                        print("This move left has not been found before")
                        next_vertex = len(self.board_objects.keys())
                        print(f"Next vertex: {next_vertex}")
                        self.board_objects[next_vertex] = temp_board
                        if self.debug_mode == 1:
                            print(self.board_objects)
                        self.piece_objects[next_vertex] = copy.deepcopy(self.piece_objects[current_vertex])
                        self.piece_objects[next_vertex][piece]['start_h'] -= 1

                        #call recursion
                        self.vertex_dict[current_vertex].append(next_vertex)
                        self.vertex_dict[next_vertex] = []
                        if self.debug_mode == 1:
                            input("Stepping to next vertex\n>")
                        self.solve_puzzle(next_vertex)
                        #reset temp board on return
                        print(f"Returned from recursive function call.\nCurrent vertex: {current_vertex} Last piece moved: {piece}\nCurrent board:")
                        self.print_board_simple(self.board_objects[current_vertex])
                        if self.debug_mode == 1:
                            input(">")
                        temp_board = copy.deepcopy(self.board_objects[current_vertex])
                    #else have found it and want to skip
                    else:
                        #has to be in list format, grab 0th element which should be the only element
                        found_vertex = [key for (key,value) in self.board_objects.items() if value == temp_board][0]
                        print(found_vertex)
                        print(f"This move left has already been found at vertex: {found_vertex}")
                        self.vertex_dict[current_vertex].append(found_vertex)
                        #reprint the board?
                        #reset temp board
                        temp_board = copy.deepcopy(self.board_objects[current_vertex])


                #check move right
                if self.piece_objects[current_vertex][piece]['start_h'] + self.piece_objects[current_vertex][piece]['length'] + 1 > self.h_size:
                    print("Can't move right, boundary issue")
                elif temp_board[self.piece_objects[current_vertex][piece]['start_v']][self.piece_objects[current_vertex][piece]['start_h'] + self.piece_objects[current_vertex][piece]['length']] != '.':
                    print("Can't move right, other piece in the way")
                else:
                    print("Temporarily moving right")
                    temp_board[self.piece_objects[current_vertex][piece]['start_v']][self.piece_objects[current_vertex][piece]['start_h']] = '.'
                    temp_board[self.piece_objects[current_vertex][piece]['start_v']][self.piece_objects[current_vertex][piece]['start_h'] + self.piece_objects[current_vertex][piece]['length']] = piece
                    self.print_board_simple(temp_board)

                    if temp_board not in self.board_objects.values():
                        print("This move right has not been found before")
                        next_vertex = len(self.board_objects.keys())
                        print(f"Next vertex: {next_vertex}")
                        self.board_objects[next_vertex] = temp_board
                        if self.debug_mode == 1:
                            print(self.board_objects)
                        self.piece_objects[next_vertex] = copy.deepcopy(self.piece_objects[current_vertex])
                        self.piece_objects[next_vertex][piece]['start_h'] += 1
                        #call recursion
                        self.vertex_dict[current_vertex].append(next_vertex)
                        self.vertex_dict[next_vertex] = []

                        #check for game over before stepping again in recursion, only on move right because x moving right is the only way to win
                        if piece == 'x':
                            #assuming length of 2
                            print(f"Checking for game over -adding 1 to start_h\nNext x starth_h: {self.piece_objects[next_vertex]['x']['start_h']} h_size: {self.h_size}")
                            if self.piece_objects[next_vertex]['x']['start_h'] + 2 == self.h_size:
                                if self.debug_mode == 1:
                                    input("This move solves the puzzle!\n>")
                                self.end_vertices.append(next_vertex)
                                print(f"Current end vertices: {self.end_vertices}")
                                break
                        # check for game over
                        if self.debug_mode == 1:
                            input("Stepping to next vertex\n>")
                        self.solve_puzzle(next_vertex)
                        #reset temp board on return
                        print(f"Returned from recursive function call.\nCurrent vertex: {current_vertex} Last piece moved: {piece}\nCurrent board:")
                        self.print_board_simple(self.board_objects[current_vertex])
                        if self.debug_mode == 1:
                            input(">")
                        temp_board = copy.deepcopy(self.board_objects[current_vertex])
                    else:
                        #has to be in list format, grab 0th element which should be the only element
                        found_vertex = [key for (key,value) in self.board_objects.items() if value == temp_board][0]
                        print(found_vertex)
                        print(f"This move right has already been found at vertex: {found_vertex}")
                        self.vertex_dict[current_vertex].append(found_vertex)
                        #reset temp board
                        temp_board = copy.deepcopy(self.board_objects[current_vertex])

            #vertical
            else:
                print(f"piece: {piece} Direction: Vertical")
                #check move up
                if self.piece_objects[current_vertex][piece]['start_v'] == 0:
                    print("Can't move up, boundary issue")
                elif temp_board[self.piece_objects[current_vertex][piece]['start_v']-1][self.piece_objects[current_vertex][piece]['start_h']] != '.':
                    print("Can't move up, other piece in the way")
                else:
                    print("Temporarily moving up")
                    temp_board[self.piece_objects[current_vertex][piece]['start_v']-1][self.piece_objects[current_vertex][piece]['start_h']] = piece
                    temp_board[self.piece_objects[current_vertex][piece]['start_v'] + self.piece_objects[current_vertex][piece]['length']-1][self.piece_objects[current_vertex][piece]['start_h']] = '.'
                    self.print_board_simple(temp_board)

                    if temp_board not in self.board_objects.values():
                        print("This move up has not been found before")
                        next_vertex = len(self.board_objects.keys())
                        print(f"Next vertex: {next_vertex}")
                        self.board_objects[next_vertex] = temp_board
                        if self.debug_mode == 1:
                            print(self.board_objects)
                        self.piece_objects[next_vertex] = copy.deepcopy(self.piece_objects[current_vertex])
                        self.piece_objects[next_vertex][piece]['start_v'] -= 1

                        #call recursion
                        self.vertex_dict[current_vertex].append(next_vertex)
                        self.vertex_dict[next_vertex] = []
                        if self.debug_mode == 1:
                            input("Stepping to next vertex\n>")
                        self.solve_puzzle(next_vertex)
                        #reset temp board on return
                        print(f"Returned from recursive function call.\nCurrent vertex: {current_vertex} Last piece moved: {piece}\nCurrent board:")
                        self.print_board_simple(self.board_objects[current_vertex])
                        if self.debug_mode == 1:
                            input(">")
                        temp_board = copy.deepcopy(self.board_objects[current_vertex])
                    else:
                        #has to be in list format, grab 0th element which should be the only element
                        found_vertex = [key for (key,value) in self.board_objects.items() if value == temp_board][0]
                        print(found_vertex)
                        print(f"This move up has already been found at vertex: {found_vertex}")
                        self.vertex_dict[current_vertex].append(found_vertex)
                        #removing this logic from all moves, not sure if I want to do this
                        #this would have removed a move that is an "undo" of the previous move, but it might remove a connection that would lead to a quicker solve
                        # if current_vertex not in self.vertex_dict[found_vertex]:
                        #     print("Adding to vertex dict, this is not reverting move")
                        #     self.vertex_dict[current_vertex].append(found_vertex)
                        # else:
                        #     print("Not adding to vertex dict, this is reverting move")
                        #reset temp board
                        temp_board = copy.deepcopy(self.board_objects[current_vertex])

                #check move down
                if self.piece_objects[current_vertex][piece]['start_v'] + self.piece_objects[current_vertex][piece]['length'] + 1 > self.v_size:
                    print("Can't move down, boundary issue")
                elif temp_board[self.piece_objects[current_vertex][piece]['start_v'] + self.piece_objects[current_vertex][piece]['length']][self.piece_objects[current_vertex][piece]['start_h']] != '.':
                    print("Can't move down, other piece in the way")
                else:
                    print("Temporarily moving Down")
                    temp_board[self.piece_objects[current_vertex][piece]['start_v']][self.piece_objects[current_vertex][piece]['start_h']] = '.'
                    temp_board[self.piece_objects[current_vertex][piece]['start_v'] + self.piece_objects[current_vertex][piece]['length']][self.piece_objects[current_vertex][piece]['start_h']] = piece
                    # print(temp_board)
                    self.print_board_simple(temp_board)

                    if temp_board not in self.board_objects.values():
                        print("This move down has not been found before")
                        next_vertex = len(self.board_objects.keys())
                        print(f"Next vertex: {next_vertex}")
                        self.board_objects[next_vertex] = temp_board
                        if self.debug_mode == 1:
                            print(self.board_objects)
                        self.piece_objects[next_vertex] = copy.deepcopy(self.piece_objects[current_vertex])
                        self.piece_objects[next_vertex][piece]['start_v'] += 1
                        #call recursion
                        self.vertex_dict[current_vertex].append(next_vertex)
                        self.vertex_dict[next_vertex] = []
                        if self.debug_mode == 1:
                            input("Stepping to next vertex\n>")
                        self.solve_puzzle(next_vertex)
                        #reset temp board on return
                        #add direction moved to this print
                        print(f"Returned from recursive function call.\nCurrent vertex: {current_vertex} Last piece moved: {piece}\nCurrent board:")
                        self.print_board_simple(self.board_objects[current_vertex])
                        if self.debug_mode == 1:
                            input(">")
                        temp_board = copy.deepcopy(self.board_objects[current_vertex])
                    else:
                        #has to be in list format, grab 0th element which should be the only element
                        found_vertex = [key for (key,value) in self.board_objects.items() if value == temp_board][0]
                        print(found_vertex)
                        print(f"This move down has already been found at vertex: {found_vertex}")
                        self.vertex_dict[current_vertex].append(found_vertex)
                        #reset temp board
                        temp_board = copy.deepcopy(self.board_objects[current_vertex])
            if self.debug_mode == 1:
                input("Continue to next piece\n>")
        if self.debug_mode == 1:
            input(f"Reached end of solve puzzle function for vertex: {current_vertex}\n>")

    def find_best_path_bfs(self):
        solution_list = []
        # print(f"Final vertex dict: {self.vertex_dict}\nExit points: {self.end_vertices}")
        b_start = time.time()
        for exit_point in self.end_vertices:
            print(f"Checking exit point: {exit_point}")
            paths = breadth_first_search.bfs_shortest_path(self.vertex_dict, 0, exit_point)
            solution_list.append(paths)
        b_end = time.time()
        self.bfs_time = round((b_end - b_start),4)
        num_solutions = len(solution_list)
        input(f"Found {num_solutions} useful solutions, time elapsed finding all solutions: {self.bfs_time} seconds\nLooking for shortest solution..\n>")
        # print("Looking for shortest solution..\nAll solutions:")
        solution_list.sort(key=len)
        shortest_len = len(solution_list[0])
        for temp_solution in solution_list:
            # print(temp_solution)
            if len(temp_solution) == shortest_len:
                self.final_solutions.append(temp_solution)


        print("Shortest solutions")
        print(self.final_solutions)
        input(">")

    #not used anymore
    def find_best_path(self):
        print(f"Final vertex dict: {self.vertex_dict}\nExit points: {self.end_vertices}\nPrinting all boards..")
        for temp_vertex in self.board_objects.keys():
            self.final_graph[temp_vertex] = set(self.vertex_dict[temp_vertex])

        input(f"final_graph: \n{self.final_graph}\n>")

        input(f"Adjacency graph\n>")
        breadth_first_search.print_graph(self.final_graph)
        input(f"Exit points: {self.end_vertices}\n>")

        for exit_point in self.end_vertices:
            print(f"Checking exit point: {exit_point}")
            solution_list = list(breadth_first_search.dfs_paths(self.final_graph, 0, exit_point))
        solution_list.sort(key=len)
        print("All solutions:")
        for temp_solution in solution_list:
            print(temp_solution)

        print("Final shortest solutions")
        shortest_len = len(solution_list[0])
        for short_solution in solution_list:
            if len(short_solution) > shortest_len:
                print("No more solutions")
                break
            print(f"Short solution: {short_solution}")
            self.final_solutions.append(short_solution)

    def print_final_solutions(self):
        os.system("cls")
        input("Printing final solutions\n>")

        for solution in self.final_solutions:
            for vertex in solution:
                os.system("cls")
                print("\n")
                self.print_board_simple(self.board_objects[vertex])
                input(">")
            input("Finished this solution\n>")
        print("Finished displaying the shortest solutions! Any one of these will win the game")


if __name__ == "__main__":
    piece_objects = Board()
