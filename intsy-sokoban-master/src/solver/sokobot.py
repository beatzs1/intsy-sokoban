import heapq
from itertools import count


class SokoBot:
    def __init__(self):
        self.board = None

    def solveSokobanPuzzle(self, width, height, mapData, itemsData):
        self.board = Board(width, height, mapData, itemsData)
        directions = ("u", "d", "l", "r")

        initial_h = self.heuristic(self.board.state)
        counter = count()

        pq = [(initial_h, 0, next(counter), self.board.state, [])]
        visited = set()

        print("Player: " + str(self.board.state.player))
        print("Crates: " + str(self.board.state.crates))
        print("Walls: " + str(self.board.walls))
        print("Goals: " + str(self.board.goals))

        while pq:
            _, g, _, current_state, path = heapq.heappop(pq)

            if self.heuristic(current_state) == 0:
                print(f"Solved in {g} moves!")
                print("Moves:", path)
                return path

            if current_state in visited:
                continue
            visited.add(current_state)

            for i, next_state in current_state.get_successors():
                if next_state in visited or self.is_deadlock(next_state):
                    continue

                new_g = g + 1
                new_h = self.heuristic(next_state)
                new_f = new_g + new_h

                new_path = path + [directions[i]]
                heapq.heappush(pq, (new_f, new_g, next(counter), next_state, new_path))

        print("No solution found.")
        return []

    def heuristic(self, state):
        unresolved_crates = state.crates - state.board.goals

        if not unresolved_crates:
            return 0

        component1 = self.closest_crate_to_player(state.player, unresolved_crates)
        component2 = self.closest_goal_to_crate(unresolved_crates, state.board.goals)

        return component1 + component2 - 1
    
    
    def is_corner_blocked(self,crates_row,crates_col):
        horizontal_blocked = False
        vertical_blocked = False
                
        for(row,column) in State.DIRECTIONS:
            #print(row,column)
                
            next_crate_row = (crates_row + row,crates_col)
            next_crate_col = (crates_row, crates_col + column)
            
            
                
            if next_crate_row in self.board.walls:
                 vertical_blocked = True
            if next_crate_col in self.board.walls:
                horizontal_blocked = True
                
                
            
                    
            if(horizontal_blocked and vertical_blocked):
                print("CORNER")
                return True
            
        return False
                
    def is_crate_at_goal(self,crate_row,crate_col):
        goals = self.board.goals
        
        for(goal_row,goal_column) in goals:
            if (crate_row,crate_col) == (goal_row,goal_column):
                return True
        return False
        
        
        
        
    def is_deadlock(self, state):
        crates = state.crates
        
        for (crates_row,crates_col) in crates:
            if self.is_crate_at_goal(crates_row,crates_col):
                continue
            
            if self.is_corner_blocked(crates_row,crates_col):
                return True
            
        return False
    
    

    def closest_crate_to_player(self, player, crates):
        return min(self.distance(player, crate) for crate in crates)

    def closest_goal_to_crate(self, crates, goals):
        if not crates:
            return 0

        return sum(
            min(self.distance(crate, goal) for goal in goals)
            for crate in crates
        )

    def distance(self, a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])


class Board:
    def __init__(self, width, height, map_data, items_data):
        self.walls = set()
        self.goals = set()

        crates = set()
        player = None

        for i in range(height):
            for j in range(width):
                if map_data[i][j] == "#":
                    self.walls.add((i, j))
                if map_data[i][j] == ".":
                    self.goals.add((i, j))
                if items_data[i][j] == "@":
                    player = (i, j)
                if items_data[i][j] == "$":
                    crates.add((i, j))

        self.state = State(self, player, frozenset(crates))


class State:
    DIRECTIONS = ((-1, 0), (1, 0), (0, -1), (0, 1))

    def __init__(self, board, player, crates):
        self.board = board
        self.player = player
        self.crates = crates

    def get_successors(self):
        successors = set()
        player_r, player_c = self.player

        for i, (dir_r, dir_c) in enumerate(self.DIRECTIONS):
            next_player_position = (
                player_r + dir_r,
                player_c + dir_c,
            )

            if next_player_position in self.board.walls:
                continue

            new_crates_positions = set(self.crates)

            if next_player_position in self.crates:
                crate_r, crate_c = next_player_position
                next_crate_position = (
                    crate_r + dir_r,
                    crate_c + dir_c,
                )

                if (
                    next_crate_position in self.board.walls
                    or next_crate_position in self.crates
                ):
                    continue

                new_crates_positions.remove(next_player_position)
                new_crates_positions.add(next_crate_position)

            successors.add(
                (
                    i,
                    State(
                        self.board,
                        next_player_position,
                        frozenset(new_crates_positions),
                    ),
                )
            )

        return successors

    def __eq__(self, other):
        if not isinstance(other, State):
            return NotImplemented
        return self.player == other.player and self.crates == other.crates

    def __hash__(self):
        return hash((self.player, self.crates))
