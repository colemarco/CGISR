import numpy as np
import networkx as nx
import matplotlib.pyplot as plt

"""
This file puts into practical use some of the graph theory fundamentals I'm relearning.
Putting them into code and applying it to CS problems is exactly the foundation needed 
throughout the rest of this ISR. This problem specifically solves sodoku using a 9 
coloring of a graph representation of the board.
"""


class SudokuGraphSolver:
    def __init__(self):
        self.board_size = 9
        self.box_size = 3

    def generate_board(self):
        """Generates a partially filled Sudoku board"""
        # Start with empty board
        board = np.zeros((9, 9), dtype=int)

        # Add some initial numbers (this is a simple example board)
        initial_numbers = [
            (0, 0, 5),
            (0, 1, 3),
            (0, 4, 7),
            (1, 0, 6),
            (1, 3, 1),
            (1, 4, 9),
            (1, 5, 5),
            (2, 1, 9),
            (2, 2, 8),
            (2, 7, 6),
            (3, 0, 8),
            (3, 4, 6),
            (3, 8, 3),
            (4, 0, 4),
            (4, 3, 8),
            (4, 5, 3),
            (4, 8, 1),
            (5, 0, 7),
            (5, 4, 2),
            (5, 8, 6),
            (6, 1, 6),
            (6, 6, 2),
            (6, 7, 8),
            (7, 3, 4),
            (7, 4, 1),
            (7, 5, 9),
            (7, 8, 5),
            (8, 4, 8),
            (8, 7, 7),
            (8, 8, 9),
        ]

        for row, col, val in initial_numbers:
            board[row][col] = val

        return board

    def display_board(self, board):
        """Displays the Sudoku board with grid lines"""
        plt.figure(figsize=(10, 10))
        plt.imshow(board, cmap="Pastel1")

        # Add grid lines
        for i in range(self.board_size + 1):
            if i % 3 == 0:
                plt.axhline(y=i - 0.5, color="black", linewidth=2)
                plt.axvline(x=i - 0.5, color="black", linewidth=2)
            else:
                plt.axhline(y=i - 0.5, color="gray", linewidth=0.5)
                plt.axvline(x=i - 0.5, color="gray", linewidth=0.5)

        # Add numbers
        for i in range(self.board_size):
            for j in range(self.board_size):
                if board[i, j] != 0:
                    plt.text(
                        j,
                        i,
                        str(int(board[i, j])),
                        ha="center",
                        va="center",
                        color="black",
                    )

        plt.xticks([])
        plt.yticks([])
        plt.title("Sudoku Board")
        plt.show()

    def create_graph(self, board):
        """Creates a graph representation of the Sudoku board"""
        G = nx.Graph()

        # Add nodes (each cell is a node)
        for i in range(self.board_size):
            for j in range(self.board_size):
                G.add_node((i, j), value=board[i][j])

        # Add edges for row constraints
        for i in range(self.board_size):
            for j in range(self.board_size):
                for k in range(j + 1, self.board_size):
                    G.add_edge((i, j), (i, k))

        # Add edges for column constraints
        for j in range(self.board_size):
            for i in range(self.board_size):
                for k in range(i + 1, self.board_size):
                    G.add_edge((i, j), (k, j))

        # Add edges for 3x3 box constraints
        for box_row in range(3):
            for box_col in range(3):
                box_nodes = [
                    (i, j)
                    for i in range(box_row * 3, (box_row + 1) * 3)
                    for j in range(box_col * 3, (box_col + 1) * 3)
                ]
                for i, node1 in enumerate(box_nodes):
                    for node2 in box_nodes[i + 1 :]:
                        G.add_edge(node1, node2)

        return G

    def display_graph(self, G, board):
        """Displays the graph with colored nodes based on initial values"""
        plt.figure(figsize=(15, 15))

        # Position nodes in a grid layout
        pos = {(i, j): (j, -i) for i in range(9) for j in range(9)}

        # Color nodes based on their values
        colors = [
            "white" if board[node] == 0 else f"C{board[node]-1}" for node in G.nodes()
        ]

        # Draw the graph
        nx.draw(
            G,
            pos=pos,
            node_color=colors,
            with_labels=False,
            node_size=500,
            font_size=10,
            font_weight="bold",
        )

        # Add value labels to nodes
        labels = {
            (i, j): str(int(board[i][j])) if board[i][j] != 0 else ""
            for i, j in G.nodes()
        }
        nx.draw_networkx_labels(G, pos, labels)

        plt.title("Graph Representation of Sudoku Board")
        plt.show()

    def solve(self, board):
        """Solves the Sudoku using graph coloring approach"""
        G = self.create_graph(board)
        solution = board.copy()

        def is_safe(node, color):
            """Check if it's safe to color a node with given color"""
            for neighbor in G.neighbors(node):
                if solution[neighbor] == color:
                    return False
            return True

        def solve_coloring(node_idx=0):
            """Recursive function to solve graph coloring"""
            if node_idx == len(G.nodes):
                return True

            # Get current node (cell position)
            node = list(G.nodes())[node_idx]

            # If already colored (has initial value), skip
            if solution[node] != 0:
                return solve_coloring(node_idx + 1)

            # Try colors 1-9
            for color in range(1, 10):
                if is_safe(node, color):
                    solution[node] = color
                    if solve_coloring(node_idx + 1):
                        return True
                    solution[node] = 0

            return False

        # Solve the puzzle
        if solve_coloring():
            return solution
        return None


solver = SudokuGraphSolver()

print("Generating initial Sudoku board...")
initial_board = solver.generate_board()
solver.display_board(initial_board)

print("\nCreating graph representation...")
G = solver.create_graph(initial_board)
solver.display_graph(G, initial_board)

print("\nSolving using graph coloring...")
solution = solver.solve(initial_board)
if solution is not None:
    print("Solution found!")
    solver.display_board(solution)
    print("\nFinal graph coloring:")
    solver.display_graph(G, solution)
else:
    print("No solution exists!")
