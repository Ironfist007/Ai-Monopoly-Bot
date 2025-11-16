from typing import List, Dict
from node import Node


class MonopolyTree:
    def __init__(self, root_node):
        self.rootNode = root_node
        self.leafs: List[Node] = []
    
    def generate_tree(self, depth: int):
        self.generate_subtree(self.rootNode, depth, 0)
        return self.rootNode
    
    def generate_subtree(self, node: Node, depth: int, current_depth: int) -> None:
        # Terminal condition: reached maximum depth
        if current_depth >= depth:
            self.leafs.append(node)
            return
        
        # Terminal condition: bankruptcy (game over)
        # Check both players for bankruptcy
        if node.current_player.balance < 0 or node.second_player.balance < 0:
            self.leafs.append(node)
            return
        
        # Terminal condition: someone won (balance > 2000)
        if node.current_player.balance > 2000 or node.second_player.balance > 2000:
            self.leafs.append(node)
            return
        
        # Generate all possible next states (children)
        next_states: List[Node] = node.get_children()
        
        # If no valid moves possible, treat as leaf
        if len(next_states) == 0:
            self.leafs.append(node)
            return
        
        # Recursively generate subtrees for all children
        # Important: For chance nodes, this generates ALL 6 dice outcomes
        # For decision nodes, this generates all possible actions
        for child_node in next_states:
            # Set parent reference for bottom-up evaluation
            child_node.parent = node
            
            # Increment round counter
            child_node.round = node.round + 1
            
            # Recursively expand this child
            self.generate_subtree(child_node, depth, current_depth + 1)