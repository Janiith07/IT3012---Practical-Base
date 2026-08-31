# agent.py
import math
import random
from collections import deque  # special queue. used here for BFS. BFS needs a FIFO queue.
import heapq  # Used for UCS. heapq gives us a priority queue, where the lowest-cost item comes first.


class SearchAgent:
    """Lab 03/04: A Goal-Based/Planning Agent. Uses BFS/DFS/UCS/A* to compute a full path
    to the nearest food pellet before acting, instead of reacting one step at a time."""

    def __init__(self):  # This runs automatically when we create a SearchAgent
        self.plan = [] # Stores the agent's current plan.
        self.active_algo = 'BFS'  # Change to 'DFS', 'UCS', or 'AStar' to compare strategies.

        # Internal dead-reckoning state (same technique as ModelBasedAgent), needed
        # because get_percept() never reveals the agent's absolute position.
        self.position = (0, 0) # Stores the agent's estimated position.
        self.facing = 'Right' # Stores which direction the agent is facing.
        self.last_action = None # Stores the previous action.
        self.previous_percept = None # Stores the previous information received from the environment.

    # --- internal facing helpers (mirrors the environment's own turn logic) ---
    def turn_left(self): # Defines a function for turning left.
        order = ['Right', 'Up', 'Left', 'Down'] # defines the direction order when turning left:
        self.facing = order[(order.index(self.facing) + 1) % 4] # finds the current direction and changes it to the next direction.

    def turn_right(self): # Defines a function for turning right.
        order = ['Right', 'Down', 'Left', 'Up']
        self.facing = order[(order.index(self.facing) + 1) % 4]

    def get_next_position(self, position=None, facing=None): # Calculates where the agent would move if it moves forward.
        if position is None:
            position = self.position # If no position is provided, use the agent's current position.
        if facing is None:
            facing = self.facing # If no direction is provided, use the agent's current direction.
        x, y = position # Separates the position into x and y.
        if facing == 'Up':  # Moving Up increases y.
            return (x, y + 1)
        elif facing == 'Down':
            return (x, y - 1)
        elif facing == 'Left':
            return (x - 1, y) # Moving Left decreases x.
        else:
            return (x + 1, y)

    def update_internal_state(self): # Updates the agent's estimated position and direction.
        """Updates estimated position/facing using the previous action + previous percept."""
        if self.last_action is None:
            return # If there was no previous action, do nothing.
        if self.last_action == 'turn_left':
            self.turn_left() # Update the agent's direction.
        elif self.last_action == 'turn_right':
            self.turn_right()
        elif self.last_action == 'move_forward': # agent tried to move forward.
            if self.previous_percept is not None and not self.previous_percept['wall_ahead']: # Do we have previous sensor information? Was there no wall ahead?
                self.position = self.get_next_position() # Update the position.

    # --- graph expansion for the search algorithms ---
    def get_neighbors(self, pos, walls, grid_size): # Finds all possible positions the agent can move to from a given position.
        x, y = pos # Gets the current x and y.
        width, height = grid_size # Gets the grid dimensions.
        candidates = [
            ('Up', (x, y + 1)),
            ('Down', (x, y - 1)),
            ('Left', (x - 1, y)),
            ('Right', (x + 1, y)),
        ]
        result = [] # Creates an empty list to store valid movements.
        for action, (nx, ny) in candidates: # Goes through each possible movement.
            if 0 <= nx < width and 0 <= ny < height and (nx, ny) not in walls: # Is x,y inside the grid, Is there no wall at that position
                result.append((action, (nx, ny))) # If the movement is valid, add it to the result.
        return result # Returns all valid neighboring positions.

    # --- BFS: FIFO queue, explores shallowest nodes first, guarantees shortest path ---
    def bfs_search(self, start_pos, goal_pos, walls, grid_size): # Defines Breadth-First Search
        walls = set(walls)# Converts walls into a set.
        frontier = deque([(start_pos, [])]) # Creates the BFS queue.
        reached = {start_pos} # Stores positions that have already been visited.
        while frontier: # Continue searching while the queue is not empty.
            pos, path = frontier.popleft() # Remove the first item from the queue.
            if pos == goal_pos:
                return path # If we reached the food, return the path.
            for action, npos in self.get_neighbors(pos, walls, grid_size): #Find all valid movements from the current position.
                if npos not in reached: # Check whether we have already visited that position.
                    reached.add(npos) # Mark it as visited.
                    frontier.append((npos, path + [action])) # Add the new position and updated path to the queue.
        return None # If no path exists, return None.

    # --- DFS: LIFO stack, explores deepest nodes first, no optimality guarantee ---
    def dfs_search(self, start_pos, goal_pos, walls, grid_size):
        walls = set(walls)
        frontier = [(start_pos, [])]
        reached = {start_pos}
        while frontier:
            pos, path = frontier.pop()
            if pos == goal_pos:
                return path
            for action, npos in self.get_neighbors(pos, walls, grid_size):
                if npos not in reached:
                    reached.add(npos)
                    frontier.append((npos, path + [action]))
        return None

    # --- UCS: priority queue ordered by path cost g(n); optimal for weighted/uniform costs ---
    def ucs_search(self, start_pos, goal_pos, walls, grid_size):
        walls = set(walls)
        counter = 0  # tie-breaker so heapq never compares tuples containing positions
        frontier = [(0, counter, start_pos, [])]
        reached = {start_pos: 0}
        while frontier:
            cost, _, pos, path = heapq.heappop(frontier)
            if pos == goal_pos:
                return path
            if cost > reached.get(pos, float('inf')):
                continue
            for action, npos in self.get_neighbors(pos, walls, grid_size):
                new_cost = cost + 1
                if npos not in reached or new_cost < reached[npos]:
                    reached[npos] = new_cost
                    counter += 1
                    heapq.heappush(frontier, (new_cost, counter, npos, path + [action]))
        return None

    # --- Lab 04: heuristic functions for A* ---
    def manhattan_distance(self, pos, goal):
        """h(n) = |x1-x2| + |y1-y2| -- exact minimum cost on a 4-way movement grid."""
        x1, y1 = pos
        x2, y2 = goal
        return abs(x1 - x2) + abs(y1 - y2)

    def euclidean_distance(self, pos, goal):
        """h(n) = sqrt((x1-x2)^2 + (y1-y2)^2) -- straight-line distance."""
        x1, y1 = pos
        x2, y2 = goal
        return math.sqrt((x1 - x2) ** 2 + (y1 - y2) ** 2)

    # --- A*: priority queue ordered by f(n) = g(n) + h(n); optimal AND explores far fewer nodes than UCS ---
    def astar_search(self, start_pos, goal_pos, walls, grid_size, heuristic_type='manhattan'):
        """A* Search. Uses the heuristic to prioritize nodes that look closer to the goal,
        drastically reducing the number of explored nodes compared to BFS/UCS."""
        walls = set(walls)
        heuristic = self.manhattan_distance if heuristic_type == 'manhattan' else self.euclidean_distance

        g_start = 0
        h_start = heuristic(start_pos, goal_pos)
        f_start = g_start + h_start

        frontier = [(f_start, g_start, start_pos, [])]
        reached_states = {}

        while frontier:
            f_cost, g_cost, current_pos, path_taken = heapq.heappop(frontier)

            if current_pos == goal_pos:
                return path_taken

            if current_pos in reached_states and reached_states[current_pos] <= g_cost:
                continue  # already found an equal-or-better path to this node
            reached_states[current_pos] = g_cost

            for action, npos in self.get_neighbors(current_pos, walls, grid_size):
                g_new = g_cost + 1
                if npos not in reached_states or g_new < reached_states[npos]:
                    h_new = heuristic(npos, goal_pos)
                    f_new = g_new + h_new
                    heapq.heappush(frontier, (f_new, g_new, npos, path_taken + [action]))

        return None  # no path exists

    # --- bridge: convert an abstract Up/Down/Left/Right path into the environment's
    # actual turn_left/turn_right/move_forward actuator commands ---
    def convert_path_to_commands(self, path):
        commands = []
        sim_facing = self.facing
        order_left = ['Right', 'Up', 'Left', 'Down']
        order_right = ['Right', 'Down', 'Left', 'Up']
        for direction in path:
            while sim_facing != direction:
                if order_left[(order_left.index(sim_facing) + 1) % 4] == direction:
                    commands.append('turn_left')
                    sim_facing = order_left[(order_left.index(sim_facing) + 1) % 4]
                else:
                    commands.append('turn_right')
                    sim_facing = order_right[(order_right.index(sim_facing) + 1) % 4]
            commands.append('move_forward')
        return commands

    def find_closest_food(self, all_food):
        if not all_food:
            return None
        return min(all_food, key=lambda f: abs(f[0] - self.position[0]) + abs(f[1] - self.position[1]))

    def sense_and_act(self, percept: dict) -> str:
        self.update_internal_state()

        if not self.plan:
            target = self.find_closest_food(percept['all_food'])
            if target is None:
                action = 'move_forward'
                self.last_action = action
                self.previous_percept = percept.copy()
                return action

            walls = percept['walls']
            grid_size = percept['grid_size']

            if self.active_algo == 'BFS':
                path = self.bfs_search(self.position, target, walls, grid_size)
            elif self.active_algo == 'DFS':
                path = self.dfs_search(self.position, target, walls, grid_size)
            elif self.active_algo == 'AStar':
                path = self.astar_search(self.position, target, walls, grid_size, heuristic_type='manhattan')
            else:
                path = self.ucs_search(self.position, target, walls, grid_size)

            self.plan = self.convert_path_to_commands(path) if path else ['move_forward']

        action = self.plan.pop(0)
        self.last_action = action
        self.previous_percept = percept.copy()
        return action


class GreedyGridAgent:
    """A simple agent that tries to move around systematically to clear the grid."""

    def __init__(self):
        self.actions_pool = ['Up', 'Down', 'Left', 'Right']

    def sense_and_act(self, percept: dict) -> str:
        # If standing directly on food, or just wander / move towards coordinates
        pos = percept['agent_pos']
        # Simple heuristic or fallback random sweep
        return random.choice(self.actions_pool)

class SimpleReflexAgent:
    """Lab 02 Step 1.2: Reacts purely to the current percept using strict IF-THEN
    condition-action rules. No __init__, no memory of past percepts or actions."""

    def sense_and_act(self, percept: dict) -> str:
        if percept['food_here']:
            return 'move_forward'
        elif percept['wall_ahead']:
            return 'turn_left'
        else:
            return 'move_forward'


class ModelBasedAgent:
    """
    Lab 02 Step 1.3

    A Model-Based Agent maintains an internal state.

    It remembers:
    - estimated position
    - estimated facing direction
    - visited cells
    - previous action
    - previous percept

    The internal state allows the agent to avoid
    repeatedly following the same path.
    """

    def __init__(self):

        # -------------------------------------------------
        # INTERNAL STATE
        # -------------------------------------------------

        # Estimated starting position
        self.position = (0, 0)

        # Environment starts facing Right
        self.facing = "Right"

        # Cells already visited
        self.visited_cells = set()

        # Previous action
        self.last_action = None

        # Previous percept
        self.previous_percept = None

        # Count visits to each estimated position
        self.visit_count = {}

    # =====================================================
    # TURN LEFT
    # =====================================================

    def turn_left(self):

        """
        Updates the internal facing direction
        after a left turn.
        """

        directions = [
            "Right",
            "Up",
            "Left",
            "Down"
        ]

        index = directions.index(
            self.facing
        )

        self.facing = directions[
            (index + 1) % 4
        ]

    # =====================================================
    # TURN RIGHT
    # =====================================================

    def turn_right(self):

        """
        Updates the internal facing direction
        after a right turn.
        """

        directions = [
            "Right",
            "Down",
            "Left",
            "Up"
        ]

        index = directions.index(
            self.facing
        )

        self.facing = directions[
            (index + 1) % 4
        ]

    # =====================================================
    # GET NEXT POSITION
    # =====================================================

    def get_next_position(
        self,
        position=None,
        facing=None
    ):

        """
        Estimates the cell directly ahead.

        This is part of the agent's internal
        transition model.
        """

        if position is None:

            position = self.position

        if facing is None:

            facing = self.facing

        x, y = position

        if facing == "Up":

            return (x, y + 1)

        elif facing == "Down":

            return (x, y - 1)

        elif facing == "Left":

            return (x - 1, y)

        else:

            return (x + 1, y)

    # =====================================================
    # UPDATE INTERNAL STATE
    # =====================================================

    def update_internal_state(self):

        """
        Updates the internal state using the
        previous action and previous percept.

        This represents the internal transition
        model of the Model-Based Agent.
        """

        # No previous action during first cycle
        if self.last_action is None:

            return

        # -------------------------------------------------
        # Previous action was TURN LEFT
        # -------------------------------------------------

        if self.last_action == "turn_left":

            self.turn_left()

        # -------------------------------------------------
        # Previous action was TURN RIGHT
        # -------------------------------------------------

        elif self.last_action == "turn_right":

            self.turn_right()

        # -------------------------------------------------
        # Previous action was MOVE FORWARD
        # -------------------------------------------------

        elif self.last_action == "move_forward":

            # Move forward only if the previous percept
            # said that there was no wall ahead.

            if (
                self.previous_percept is not None
                and not self.previous_percept["wall_ahead"]
            ):

                self.position = self.get_next_position()

    # =====================================================
    # SENSE AND ACT
    # =====================================================

    def sense_and_act(
        self,
        percept: dict
    ) -> str:

        # -------------------------------------------------
        # 1. UPDATE INTERNAL STATE
        # -------------------------------------------------

        self.update_internal_state()

        # -------------------------------------------------
        # 2. RECORD CURRENT ESTIMATED POSITION
        # -------------------------------------------------

        self.visited_cells.add(
            self.position
        )

        self.visit_count[self.position] = (
            self.visit_count.get(
                self.position,
                0
            ) + 1
        )

        # -------------------------------------------------
        # 3. FOOD RULE
        # -------------------------------------------------

        # IF food is here
        # THEN move forward.

        if percept["food_here"]:

            action = "move_forward"

            self.last_action = action

            self.previous_percept = percept.copy()

            return action

        # -------------------------------------------------
        # 4. WALL RULE
        # -------------------------------------------------

        if percept["wall_ahead"]:

            # If we just turned left and are still
            # facing a blocked direction, turn right.
            #
            # This prevents repeatedly turning left.

            if self.last_action == "turn_left":

                action = "turn_right"

            else:

                action = "turn_left"

            self.last_action = action

            self.previous_percept = percept.copy()

            return action

        # -------------------------------------------------
        # 5. CHECK WHETHER NEXT CELL WAS VISITED
        # -------------------------------------------------

        next_position = self.get_next_position()

        if next_position in self.visited_cells:

            # We are about to enter a previously
            # visited cell, so change direction.

            if self.last_action == "turn_left":

                action = "turn_right"

            else:

                action = "turn_left"

            self.last_action = action

            self.previous_percept = percept.copy()

            return action

        # -------------------------------------------------
        # 6. MOVE TO A NEW CELL
        # -------------------------------------------------

        action = "move_forward"

        self.last_action = action

        self.previous_percept = percept.copy()

        return action


if __name__ == "__main__":
    sa = SearchAgent()
    print("Manhattan distance (0,0) -> (3,4):", sa.manhattan_distance((0, 0), (3, 4)))
    print("Euclidean distance (0,0) -> (3,4):", sa.euclidean_distance((0, 0), (3, 4)))