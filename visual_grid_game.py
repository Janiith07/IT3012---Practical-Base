# visual_grid_game.py
import random
import tkinter as tk


class VisualGridHuntGame:  # manages the environment logic.
    """A flexible Pacman-style grid environment with support for configurable opponents and larger scales."""

    def __init__(self, width=10, height=10, num_food=10, num_opponents=2, custom_walls=None): # These are only default values. After user assign values these values are replaced.

        # Store the grid dimensions.
        self.width = width
        self.height = height

        self.agent_pos = [0, 0]  # Agent starts at the bottom-left corner (x=0, y=0).

        if custom_walls is not None:  # If custom walls are provided, use them.
            self.walls = set(custom_walls)
        else:
            # Otherwise use the default wall locations.
            self.walls = {(2, 2), (2, 3), (5, 5), (6, 5), (3, 7)}


        # -----------------------------
        # Generate Food
        # -----------------------------

        self.food_positions = set() # Create an empty set to store food locations.

        while len(self.food_positions) < num_food:  # Keep generating food until the required number is reached.

            # Generate random x,y coordinates.
            fx = random.randint(0, self.width - 1)
            fy = random.randint(0, self.height - 1)
            
            pos_tuple = (fx, fy) # Store the position as a tuple.

            if pos_tuple != (0, 0) and pos_tuple not in self.walls: # Food cannot be placed: At the agent's starting position and Inside a wall.
                self.food_positions.add(pos_tuple) # Add the food position.

        # -----------------------------
        # Generate Toxic Traps
        # -----------------------------

        # Create an empty set to store trap locations.
        self.toxic_traps = set()

        # Number of traps to generate.
        num_traps = 5

        # Generate random trap positions.
        while len(self.toxic_traps) < num_traps: # Keep generating traps until the required number is reached.

            # Generate random x,y coordinates.
            tx = random.randint(0, self.width - 1)
            ty = random.randint(0, self.height - 1)

            trap_pos = (tx, ty) # Store trap position.

            
            if trap_pos != (0, 0) and trap_pos not in self.walls and trap_pos not in self.food_positions: # Trap cannot be: Agent starting position, Wall, Food
                self.toxic_traps.add(trap_pos) # Add the trap position.

        # -----------------------------
        # Generate Opponents
        # -----------------------------

        self.opponents = [] # Create an empty list to store opponents.

        while len(self.opponents) < num_opponents: # Keep generating opponents until the required number is reached.

            # Generate random x,y coordinates.
            ox = random.randint(0, self.width - 1)
            oy = random.randint(0, self.height - 1)

            op_pos = [ox, oy] # Store opponent position.

            if tuple(op_pos) != (0, 0) and tuple(op_pos) not in self.walls and tuple(op_pos) not in self.food_positions:
            # Opponent cannot start:On the agent, Inside a wall, On a food location.
                self.opponents.append(op_pos) # Add the opponent.


        # -----------------------------
        # Game Statistics
        # -----------------------------
        self.score = 0 # Initial score.
        self.steps = 0 # Number of actions performed.
        self.collision = False # No collision at the beginning.

    def get_percept(self) -> dict: # Sensors
        
        # Returns everything the agent can currently observe.
        # This represents the Sensors (S) in the PEAS framework.
    
        return {
            'agent_pos': list(self.agent_pos), # Current position of the agent.
            'opponent_positions': [list(op) for op in self.opponents], # Positions of all opponents.
            'smells_food': tuple(self.agent_pos) in self.food_positions, # Check if the agent is currently standing on food.
            'smells_toxin': tuple(self.agent_pos) in self.toxic_traps, # Check if the agent is currently standing on a toxic trap.
            'hit_wall': tuple(self.agent_pos) in self.walls, # Check if the agent is currently on a wall.
            'collision': self.collision, # Whether the agent collided with an opponent.
            'score': self.score, # Current performance score.
            'remaining_food': len(self.food_positions) # Number of food items remaining.
        }

    def execute_action(self, action: str): # Actuators
    
        # Executes the action chosen by the agent.
        # This represents the Actuators (A) in the PEAS framework.
        
        self.steps += 1 # Increase the number of steps taken.
        new_pos = list(self.agent_pos) # Copy the current position before moving.

        # -----------------------------
        # Agent Movement
        # -----------------------------

        if action == 'Up':  # Move Up (increase y-coordinate).
            new_pos[1] = min(self.height - 1, new_pos[1] + 1)
        elif action == 'Down': # Move Down (decrease y-coordinate).
            new_pos[1] = max(0, new_pos[1] - 1)
        elif action == 'Left': # Move Left (decrease x-coordinate).
            new_pos[0] = max(0, new_pos[0] - 1)
        elif action == 'Right': # Move Right (increase x-coordinate).
            new_pos[0] = min(self.width - 1, new_pos[0] + 1)

            # Coordinate reference:
            # new_pos[0]  → x-coordinate 
            # new_pos[1]  → y-coordinate

        if tuple(new_pos) in self.walls: # If the new position is a wall, reduce the score and keep the agent in the same place.
            self.score -= 5
        else:
            self.agent_pos = new_pos # Otherwise move the agent.

        # -----------------------------
        # Food Collection
        # -----------------------------

        tuple_pos = tuple(self.agent_pos) # Convert the agent position to a tuple because food positions are stored as tuples.

        if tuple_pos in self.food_positions: # Check whether food exists at the current position.
            self.food_positions.remove(tuple_pos) # Remove the collected food.
            self.score += 20  # Reward the agent.

        # -----------------------------
        # Toxic Trap Penalty
        # -----------------------------

        if tuple_pos in self.toxic_traps: # Check whether the agent is on a toxic trap.
            self.score -= 15 # Penalize the agent.

        # -----------------------------
        # Opponent Movement
        # -----------------------------

        # So the opponents aren't controlled by an intelligent algorithm here—they move randomly.
        for op in self.opponents:
            move = random.choice(['Up', 'Down', 'Left', 'Right', 'Stay']) # Randomly choose an action.
            if move == 'Up' and op[1] < self.height - 1:
                op[1] += 1
            elif move == 'Down' and op[1] > 0:
                op[1] -= 1
            elif move == 'Left' and op[0] > 0:
                op[0] -= 1
            elif move == 'Right' and op[0] < self.width - 1:
                op[0] += 1

            # -----------------------------
            # Collision Detection
            # -----------------------------

            if op == self.agent_pos: # Did an opponent move onto the agent's position?
                self.score -= 50 # Penalize the agent.
                self.collision = True #  # Record the collision., This eventually ends the game.

    def is_done(self) -> bool: # Checks whether the game should end.
        return len(self.food_positions) == 0 or self.steps >= 60 or self.collision  # There are three ways the game ends.
    # End the game if: All food has been collected, or The agent has taken 60 steps, or A collision has occurred.


class GridGameGUI: # creates the visual interface.
    """Tkinter wrapper that dynamically scales cell sizes to keep larger grids on screen."""

    def __init__(self, root, width=10, height=10, num_food=12, num_opponents=2, walls=None): # These are only default values. After user assign values these values are replaced.
        self.root = root # Stores the main window.
        self.root.title("IT3012 - Scalable Multi-Agent Grid Hunt")

        self.env = VisualGridHuntGame(width=width, height=height, num_food=num_food, num_opponents=num_opponents,
                                      custom_walls=walls)

        # Dynamically calculate cell size so the total canvas fits nicely within a 600x600 window ceiling
        max_canvas_dim = 600
        self.cell_size = max(20, min(max_canvas_dim // self.env.width, max_canvas_dim // self.env.height))

        canvas_w = self.env.width * self.cell_size
        canvas_h = self.env.height * self.cell_size

        self.canvas = tk.Canvas(root, width=canvas_w, height=canvas_h, bg="white")
        self.canvas.pack()

        self.label = tk.Label(root, text="Score: 0 | Steps: 0", font=("Arial", 14))
        self.label.pack(pady=10)

        self.btn = tk.Button(root, text="Start Simulation", command=self.run_loop, font=("Arial", 12), bg="#000066",
                             fg="white")
        self.btn.pack(pady=5)

        self.draw_grid()

    def draw_grid(self):
        self.canvas.delete("all") # Deletes everything currently displayed.

        for x in range(self.env.width):
            for y in range(self.env.height):
                x1 = x * self.cell_size
                y1 = (self.env.height - 1 - y) * self.cell_size
                x2 = x1 + self.cell_size
                y2 = y1 + self.cell_size

                color = "#f1f5f9" if (x, y) not in self.env.walls else "#64748b"
                self.canvas.create_rectangle(x1, y1, x2, y2, fill=color, outline="#cbd5e1")

                # Only draw text if cell is large enough
                if self.cell_size >= 40 and (x, y) in self.env.walls:
                    self.canvas.create_text(x1 + self.cell_size / 2, y1 + self.cell_size / 2, text="W", fill="white",
                                            font=("Arial", 8, "bold"))

        for fx, fy in self.env.food_positions:
            offset = self.cell_size * 0.25
            x1 = fx * self.cell_size + offset
            y1 = (self.env.height - 1 - fy) * self.cell_size + offset
            self.canvas.create_oval(x1, y1, x1 + self.cell_size * 0.5, y1 + self.cell_size * 0.5, fill="#f59e0b",
                                    outline="#d97706")

        # Draw toxic traps
        for tx, ty in self.env.toxic_traps:

            offset = self.cell_size * 0.25
            x1 = tx * self.cell_size + offset
            y1 = (self.env.height - 1 - ty) * self.cell_size + offset

            self.canvas.create_rectangle(x1, y1, x1 + self.cell_size * 0.5, y1 + self.cell_size * 0.5, fill="purple",
                                        outline="darkviolet")

        for ox, oy in self.env.opponents:
            offset = self.cell_size * 0.2
            x1 = ox * self.cell_size + offset
            y1 = (self.env.height - 1 - oy) * self.cell_size + offset
            self.canvas.create_rectangle(x1, y1, x1 + self.cell_size * 0.6, y1 + self.cell_size * 0.6, fill="#990000",
                                         outline="#7a0000")

        ax, ay = self.env.agent_pos
        offset = self.cell_size * 0.15
        x1 = ax * self.cell_size + offset
        y1 = (self.env.height - 1 - ay) * self.cell_size + offset
        self.canvas.create_oval(x1, y1, x1 + self.cell_size * 0.7, y1 + self.cell_size * 0.7, fill="#000066",
                                outline="#1e3a8a")

    def run_loop(self):
        self.btn.config(state="disabled")

        def step():
            if not self.env.is_done():
                action = random.choice(['Up', 'Down', 'Left', 'Right'])
                self.env.execute_action(action)  # Sends the selected action to the environment.

                self.draw_grid() # Updates the GUI to show the new positions.
                self.label.config(text=f"Score: {self.env.score} | Steps: {self.env.steps} | Action: {action}")
                self.root.after(250, step) # Wait 250 milliseconds, then call step() again.
            else: # When the game ends
                end_text = f"Collision! Game Over! Final Score: {self.env.score}" if self.env.collision else f"Finished! Final Score: {self.env.score}"
                self.label.config(text=end_text)
                self.btn.config(state="normal") # Enables the Start button again.

        step() # Starts the simulation.


if __name__ == "__main__":
    root = tk.Tk() # Creates the main GUI window.
    # Try a larger grid size like 12x12 with 15 food and 3 opponents!
    app = GridGameGUI(root, width=12, height=12, num_food=15, num_opponents=0) # num_opponents=0 this specific execution is actually Single-Agent, not Multi-Agent.
    root.mainloop()