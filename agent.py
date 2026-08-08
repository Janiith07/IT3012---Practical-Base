# agent.py
import random


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