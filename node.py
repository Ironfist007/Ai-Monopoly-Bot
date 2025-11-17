import collections
import copy
from board_config import BOARD_LAYOUT

# Mapping of board position to property/space name
POSITION_TO_SPACE = {i: BOARD_LAYOUT[i] for i in range(40)}

# Special spaces that cannot be bought/sold/taxed
SPECIAL_SPACES = {
    0: "GO",
    2: "Community Chest",
    4: "Income Tax",
    7: "Chance",
    10: "JAIL",
    17: "Community Chest",
    20: "FREE PARKING",
    22: "Chance",
    30: "GO TO JAIL",
    33: "Community Chest",
    36: "Chance",
    38: "Luxury Tax"
}

# Purchasable property positions (exclude corners and special spaces)
PURCHASABLE_POSITIONS = [i for i in range(40) if i not in SPECIAL_SPACES]


class Node:
    def __init__(self, properties, current_player, second_player, node_type, parent):
        self.current_player = current_player
        self.second_player = second_player
        self.properties = properties
        self.node_type = node_type
        self.children: list[Node] = []
        self.parent: Node = parent
        self.action = []
        self.zero_value = 0
        self.one_value = 0
        self.round = 0

    def get_property_at_position(self, position, properties):
        """Find property object at given board position"""
        space_name = POSITION_TO_SPACE.get(position)
        if space_name:
            for prop in properties:
                if prop.name == space_name:
                    return prop
        return None

    def utility(self):
        one = self.second_player if self.second_player.ID == 1 else self.current_player
        zero = self.current_player if self.current_player.ID == 0 else self.second_player
        property_value_zero = sum(
            prop.value for prop in zero.properties)
        rent_earned_zero = sum(
            prop.rent for prop in zero.properties)

        property_value_one = sum(prop.value for prop in one.properties)
        # calculate the total rent earned by player from properties
        rent_earned_one = sum(prop.rent for prop in one.properties)

        self.zero_value = property_value_zero + 10 * rent_earned_zero + zero.balance
        self.one_value = property_value_one + 10 * rent_earned_one + one.balance

        if zero.balance < 200:
            self.zero_value = property_value_zero + 10 * rent_earned_zero + 10000 * zero.balance
        if one.balance < 200:
            self.one_value = property_value_one + 10 * rent_earned_one + 10000 * one.balance
        return self.zero_value, self.one_value

    @staticmethod
    def Eval(tree):
        # First, evaluate all leaf nodes
        for node in tree.leafs:
            node.utility()
        
        # Get parents of all leaf nodes
        parent_nodes = set(i.parent for i in tree.leafs if i.parent is not None)
        
        # Bottom-up traversal until we reach the root
        while len(parent_nodes) > 0:
            new_parent_nodes = set()
            
            for node in parent_nodes:
                # Skip if node has no children or children aren't fully evaluated yet
                if not hasattr(node, 'action') or len(node.action) == 0:
                    if node.parent is not None:
                        new_parent_nodes.add(node.parent)
                    continue
                
                # Get all children from the action list
                children = [child_node for _, child_node in node.action]
                
                # Ensure all children have been evaluated
                if not all(hasattr(child, 'zero_value') and hasattr(child, 'one_value') 
                        for child in children):
                    # Skip this node for now, will process in next iteration
                    new_parent_nodes.add(node)
                    continue
                
                if node.node_type == "chance":
                    # CHANCE NODE: Expected value (weighted average)
                    # For a fair 6-sided die, each outcome has probability 1/6
                    num_children = len(children)
                    
                    if num_children > 0:
                        node.zero_value = sum(child.zero_value for child in children) / num_children
                        node.one_value = sum(child.one_value for child in children) / num_children
                    else:
                        # No children means terminal/error state
                        node.zero_value = 0
                        node.one_value = 0
                
                else:
                    # DECISION NODE: Minimax logic
                    # Each player maximizes their own utility
                    
                    if node.current_player.ID == 0:
                        # Player 0's turn: chooses action that maximizes zero_value
                        node.zero_value = max(child.zero_value for child in children)
                        # Player 1's perspective: gets the one_value corresponding to Player 0's best choice
                        # Find which child Player 0 will choose
                        best_child_for_p0 = max(children, key=lambda c: c.zero_value)
                        node.one_value = best_child_for_p0.one_value
                    
                    else:  # node.current_player.ID == 1
                        # Player 1's turn: chooses action that maximizes one_value
                        node.one_value = max(child.one_value for child in children)
                        # Player 0's perspective: gets the zero_value corresponding to Player 1's best choice
                        # Find which child Player 1 will choose
                        best_child_for_p1 = max(children, key=lambda c: c.one_value)
                        node.zero_value = best_child_for_p1.zero_value
                
                # Add this node's parent to the next level (moving up the tree)
                if node.parent is not None:
                    new_parent_nodes.add(node.parent)
            
            # Move up one level in the tree
            parent_nodes = new_parent_nodes

    def levelOrderTraversal(self):
        ans = []

        # Return Null if the tree is empty
        if self is None:
            return ans

        # Initialize queue
        queue: collections.deque[Node] = collections.deque()
        queue.append(self)

        # Iterate over the queue until it's empty
        while queue:
            # Check the length of queue
            currSize = len(queue)
            currList = []

            while currSize > 0:
                # Dequeue element
                currNode = queue.popleft()
                currList.append(currNode)
                currSize -= 1

                # Check for left child
                for node in currNode.children:
                    if node is not None:
                        queue.append(node)

            # Append the currList to answer after each iteration
            ans.append(currList)

        # Return answer list
        return ans

    def get_children(self):
        if self.node_type == "chance":
            for i in range(1, 7):
                cp_properties = copy.deepcopy(self.properties)
                cp_current_player = copy.deepcopy(self.current_player)
                cp_second_player = copy.deepcopy(self.second_player)

                # Handle jail turns deterministically: no movement while in jail.
                if cp_current_player.in_jail:
                    cp_current_player.jail_turns += 1
                    if cp_current_player.jail_turns >= 3:
                        # Auto-pay fine and leave jail; movement starts next turn
                        if cp_current_player.balance >= 50:
                            cp_current_player.balance -= 50
                        cp_current_player.in_jail = False
                        cp_current_player.jail_turns = 0
                    # No movement this turn while in jail
                else:
                    # Normal movement
                    old_position = cp_current_player.position
                    cp_current_player.position = (cp_current_player.position + i) % 40  # 40 spaces on board

                    # Passing GO awards $200
                    if cp_current_player.position < old_position:
                        cp_current_player.balance += 200

                    # Landing on GO TO JAIL (index 30) sends to JAIL (index 10)
                    if cp_current_player.position == 30:
                        cp_current_player.go_to_jail()
                    
                    # Landing on Luxury Tax (index 38)
                    elif cp_current_player.position == 38:
                        cp_current_player.balance -= 75
                    
                    # Landing on Community Chest (indices 2, 17, 33) - apply based on dice
                    elif cp_current_player.position in [2, 17, 33]:
                        if i <= 2:
                            cp_current_player.balance += 100  # Reward
                        elif i <= 4:
                            cp_current_player.balance -= 50   # Penalty
                        else:  # i in [5, 6]
                            cp_current_player.position = 0    # Go to GO
                            cp_current_player.balance += 200   # Collect $200
                    
                    # Landing on Chance (indices 7, 22, 36) - apply special action based on dice
                    elif cp_current_player.position in [7, 22, 36]:
                        if i == 1:
                            cp_current_player.balance += 10  # Beauty contest
                        elif i == 2:
                            # Grand opera - collect $50 from every other player
                            cp_current_player.balance += 50
                            cp_second_player.balance -= 50
                        elif i == 3:
                            cp_current_player.go_to_jail()  # Go to jail
                        elif i == 4:
                            cp_current_player.position = 24  # Illinois Ave (position 24)
                        elif i == 5:
                            cp_current_player.balance -= 200  # Pay bank $200
                        elif i == 6:
                            cp_current_player.position = 0    # Advance to GO
                            cp_current_player.balance += 200   # Collect $200

                new_node = Node(cp_properties, cp_current_player, cp_second_player, node_type="non-chance", parent=self)
                self.action.append((i, new_node))
                self.children.append(new_node)

        else:
            # Decision node - handle current position
            current_pos = self.current_player.position
            space_name = POSITION_TO_SPACE.get(current_pos)
            
            # Income Tax decision
            if current_pos == 4:  # Income Tax
                # Option 1: Pay $200
                cp_properties_tax1 = copy.deepcopy(self.properties)
                cp_current_player_tax1 = copy.deepcopy(self.current_player)
                cp_second_player_tax1 = copy.deepcopy(self.second_player)
                cp_current_player_tax1.balance -= 200
                new_node_tax1 = Node(cp_properties_tax1, cp_second_player_tax1, cp_current_player_tax1, node_type="chance", parent=self)
                self.action.append(("income_tax_200", new_node_tax1))
                self.children.append(new_node_tax1)
                
                # Option 2: Pay 10% of net worth (whichever is cheaper)
                cp_properties_tax2 = copy.deepcopy(self.properties)
                cp_current_player_tax2 = copy.deepcopy(self.current_player)
                cp_second_player_tax2 = copy.deepcopy(self.second_player)
                net_worth = cp_current_player_tax2.balance + sum(prop.value for prop in cp_current_player_tax2.properties)
                tax_amount = int(net_worth * 0.1)
                tax_to_pay = min(200, tax_amount)
                cp_current_player_tax2.balance -= tax_to_pay
                new_node_tax2 = Node(cp_properties_tax2, cp_second_player_tax2, cp_current_player_tax2, node_type="chance", parent=self)
                self.action.append(("income_tax_percent", new_node_tax2))
                self.children.append(new_node_tax2)
            
            else:
                # Buy option
                cp_properties_buy = copy.deepcopy(self.properties)
                cp_current_player_buy = copy.deepcopy(self.current_player)
                cp_second_player_buy = copy.deepcopy(self.second_player)
                
                if current_pos in PURCHASABLE_POSITIONS:
                    current_property = self.get_property_at_position(current_pos, cp_properties_buy)
                    if current_property and current_property.owner is None and cp_current_player_buy.balance >= current_property.value:
                        cp_current_player_buy.buy(current_property)
                        new_node = Node(cp_properties_buy, cp_second_player_buy, cp_current_player_buy, node_type="chance", parent=self)
                        self.action.append(("buy", new_node))
                        self.children.append(new_node)
                
                # Sell option
                cp_properties_sell = copy.deepcopy(self.properties)
                cp_current_player_sell = copy.deepcopy(self.current_player)
                cp_second_player_sell = copy.deepcopy(self.second_player)
                
                if current_pos in PURCHASABLE_POSITIONS:
                    current_property = self.get_property_at_position(current_pos, cp_properties_sell)
                    if current_property and current_property.owner == cp_current_player_sell.ID:
                        cp_current_player_sell.sell(current_property)
                        new_node = Node(cp_properties_sell, cp_second_player_sell, cp_current_player_sell, node_type="chance", parent=self)
                        self.action.append(("sell", new_node))
                        self.children.append(new_node)
                
                # Check if on opponent's property - RENT IS MANDATORY
                if current_pos in PURCHASABLE_POSITIONS:
                    current_property = self.get_property_at_position(current_pos, self.properties)
                    if current_property and current_property.owner is not None and current_property.owner != self.current_player.ID:
                        # MANDATORY: Pay rent to the property owner
                        cp_properties_rent = copy.deepcopy(self.properties)
                        cp_current_player_rent = copy.deepcopy(self.current_player)
                        cp_second_player_rent = copy.deepcopy(self.second_player)
                        
                        # Owner is always the second_player (since owner != current_player)
                        rent_amount = current_property.rent
                        cp_current_player_rent.balance -= rent_amount
                        cp_second_player_rent.balance += rent_amount
                        
                        new_node = Node(cp_properties_rent, cp_second_player_rent, cp_current_player_rent, node_type="chance", parent=self)
                        self.action.append(("pay_rent", new_node))
                        self.children.append(new_node)
                        # Return early - rent is mandatory, no other options
                        return self.children
                
                # Do nothing (only available if NOT on opponent's property)
                cp_properties_nothing = copy.deepcopy(self.properties)
                cp_current_player_nothing = copy.deepcopy(self.current_player)
                cp_second_player_nothing = copy.deepcopy(self.second_player)
                new_node = Node(cp_properties_nothing, cp_second_player_nothing, cp_current_player_nothing, node_type="chance", parent=self)
                self.action.append(("nothing", new_node))
                self.children.append(new_node)

        return self.children
