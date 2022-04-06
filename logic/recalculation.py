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
                
node1 = Node(1)
node2 = Node(2)
node3 = Node(3)
node4 = Node(4)
node5 = Node(5)
node6 = Node(6)

node1.children = [node2, node3]
node2.children = [node6, node5]
node3.children = [node4]

for n in node1.breadth_first():
    print(n.payload)

