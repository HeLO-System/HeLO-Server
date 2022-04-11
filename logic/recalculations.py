"""
tree structure of matches that will be traversed by a breadth-first search algorithm
to recalculate all match results and scores from a certain root match
"""

class Node:

    def __init__(self, payload):
        # all the data necessary to recalculate the scores
        self.payload = payload
        self.children = []
        self.visited = False

    def add_child(self, node):
        self.children.append(node)

    # see: https://algotree.org/algorithms/tree_graph_traversal/breadth_first_search/
    def breadth_first(self):
        queue = [self]
        self.visited = True
        while queue:
            n = queue.pop(0)
            yield n
            for child in n.children:
                if not child.visited:
                    queue.append(child)
