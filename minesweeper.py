import itertools
import random


class Minesweeper():
    """
    Minesweeper game representation
    """

    def __init__(self, height=8, width=8, mines=8):

        # Set initial width, height, and number of mines
        self.height = height
        self.width = width
        self.mines = set()

        # Initialize an empty field with no mines
        self.board = []
        for i in range(self.height):
            row = []
            for j in range(self.width):
                row.append(False)
            self.board.append(row)

        # Add mines randomly
        while len(self.mines) != mines:
            i = random.randrange(height)
            j = random.randrange(width)
            if not self.board[i][j]:
                self.mines.add((i, j))
                self.board[i][j] = True

        # At first, player has found no mines
        self.mines_found = set()

    def print(self):
        """
        Prints a text-based representation
        of where mines are located.
        """
        for i in range(self.height):
            print("--" * self.width + "-")
            for j in range(self.width):
                if self.board[i][j]:
                    print("|X", end="")
                else:
                    print("| ", end="")
            print("|")
        print("--" * self.width + "-")

    def is_mine(self, cell):
        i, j = cell
        return self.board[i][j]

    def nearby_mines(self, cell):
        """
        Returns the number of mines that are
        within one row and column of a given cell,
        not including the cell itself.
        """

        # Keep count of nearby mines
        count = 0

        # Loop over all cells within one row and column
        for i in range(cell[0] - 1, cell[0] + 2):
            for j in range(cell[1] - 1, cell[1] + 2):

                # Ignore the cell itself
                if (i, j) == cell:
                    continue

                # Update count if cell in bounds and is mine
                if 0 <= i < self.height and 0 <= j < self.width:
                    if self.board[i][j]:
                        count += 1

        return count

    def won(self):
        """
        Checks if all mines have been flagged.
        """
        return self.mines_found == self.mines



#Totally correct.
#More logic can be added to known_mines & known_safes function.
class Sentence():
    """
    Logical statement about a Minesweeper game
    A sentence consists of a set of board cells,
    and a count of the number of those cells which are mines.
    """

    def __init__(self, cells, count):
        self.cells = set(cells)
        self.count = count

    def __eq__(self, other):
        return self.cells == other.cells and self.count == other.count

    def __str__(self):
        return f"{self.cells} = {self.count}"

    def known_mines(self):
        """
        Returns the set of all cells in self.cells known to be mines.
        """
        ### if number of cells be l.e to count, they are all mines
        if len(self.cells) <= self.count and len(self.cells) > 0: # number of cells shouldn't be 0
            # print(f"These are mines in {self}")
            return self.cells.copy()
        return set()

    def known_safes(self):
        """
        Returns the set of all cells in self.cells known to be safe.
        """
        if self.count == 0 and len(self.cells) > 0: # number of cells shouldn't be 0
            # print(f"These are safes in {self}")
            return self.cells.copy()
        return set()

    def mark_mine(self, cell):
        """
        Updates internal knowledge representation given the fact that
        a cell is known to be a mine.
        """
        if cell in self.cells:
            print(f"{cell} is mine in sentence {self}")
            with open('result', 'a') as f:
                f.write(f"{cell} is mine in sentence {self}\n")
            self.cells.remove(cell)
            self.count -= 1
            if self.cells == set():
                self.count = 0

    def mark_safe(self, cell):
        """
        Updates internal knowledge representation given the fact that
        a cell is known to be safe.
        """
        if cell in self.cells:
            print(f"{cell} is safe in sentence {self}")
            with open('result', 'a') as f:
                f.write(f"{cell} is safe in sentence {self}\n")
            self.cells.remove(cell)
            if self.cells == set():
                self.count = 0


class MinesweeperAI():
    """
    Minesweeper game player
    """

    def __init__(self, height=8, width=8):

        # Set initial height and width
        self.height = height
        self.width = width

        # Keep track of which cells have been clicked on
        self.moves_made = set()

        # Keep track of cells known to be safe or mines
        self.mines = set()
        self.safes = set()

        # List of sentences about the game known to be true
        self.knowledge = []

    def mark_mine(self, cell):
        """
        Marks a cell as a mine, and updates all knowledge
        to mark that cell as a mine as well.
        """
        self.mines.add(cell)
        for sentence in self.knowledge:
            sentence.mark_mine(cell)

    def mark_safe(self, cell):
        """
        Marks a cell as safe, and updates all knowledge
        to mark that cell as safe as well.
        """
        self.safes.add(cell)
        for sentence in self.knowledge:
            sentence.mark_safe(cell)

    def add_knowledge(self, cell, count):
        """
        Called when the Minesweeper board tells us, for a given
        safe cell, how many neighboring cells have mines in them.

        This function should:
            1) mark the cell as a move that has been made
            2) mark the cell as safe
            3) add a new sentence to the AI's knowledge base
               based on the value of `cell` and `count`
            4) mark any additional cells as safe or as mines
               if it can be concluded based on the AI's knowledge base
            5) add any new sentences to the AI's knowledge base
               if they can be inferred from existing knowledge
        """   
        with open('result', 'a') as f:
            f.write(f"{cell} {count}\n")
        self.moves_made.add(cell)
        self.mark_safe(cell) # add cell to safe cells and remove it from cells of all senteces
        cell_neighbors = self.get_neighbors(cell) #get neighbors of the cell
        if len(cell_neighbors) > 0: #if a neigbors which is not mine nor safe exists
            if len(cell_neighbors) <= count: #if number of cells be less than the count, they are all mines
                for c in cell_neighbors:
                    self.mark_mine(c)
            else:
                sentence = Sentence(cell_neighbors, count)
                with open('result', 'a') as f:
                    f.write(f"add_knowledge: {sentence}\n")
                print(f"add_knowledge: {sentence}")
                if not sentence in self.knowledge: # if knowledge exitsed before just ignore it
                    self.knowledge.append(sentence)
        self.infer_safeness_or_mineness()
        self.infer_knowledge_subset()
        # Delete unecessary knowledges
        new_knowledge = []
        for sentence in self.knowledge:
            if len(sentence.cells) > 0 and sentence.count >= 0:
                new_knowledge.append(sentence)
        self.knowledge = new_knowledge
        
        with open('result', 'a') as f:
            f.write(f"known safes: {self.safes}")
            f.write("\n")
            f.write(f"known mines: {self.mines}")
            f.write("\n")
            print(f"known safes: {self.safes}")
            print(f"known mines: {self.mines}")
            f.write("Knowledge:\n")
            print("Knowledge:")
            for sentence in self.knowledge:
                f.write(f"{sentence}")
                f.write("\n")
                print(sentence)
            f.write("8" * 10 + "\n")
            print("*" * 10)
        
    def infer_knowledge_subset(self):
        """
        Infere new sentences using subset method (if possible).

        Returns
        -------
        None.

        """
        for sentence1 in self.knowledge:
            for sentence2 in self.knowledge:
                if sentence1 != sentence2:
                    if len(sentence1.cells) != 0 and len(sentence2.cells) != 0:
                        if sentence1.cells <= sentence2.cells:
                            new_sentence = Sentence(sentence2.cells-sentence1.cells, sentence2.count-sentence1.count)
                            if not new_sentence in self.knowledge and new_sentence.count >= 0:
                                self.knowledge.append(new_sentence)
                                with open('result', 'a') as f:
                                    f.write(f"subset knowledge from {sentence2} and {sentence1}\n")
                                    f.write(f"new subset knowledge: {new_sentence}\n")
                                    print(f"subset knowledge from {sentence2} and {sentence1}")
                                    print(f"new subset knowledge: {new_sentence}")
                        elif sentence1.cells >= sentence2.cells:
                            new_sentence = Sentence(sentence1.cells-sentence2.cells, sentence1.count-sentence2.count)
                            if not new_sentence in self.knowledge and new_sentence.count >= 0:
                                self.knowledge.append(new_sentence)
                                with open('result', 'a') as f:
                                    f.write(f"subset knowledge from {sentence1} and {sentence2}\n")
                                    f.write(f"subset knowledge: {new_sentence}")
                                    print(f"subset knowledge from {sentence1} and {sentence2}")
                                    print(f"subset knowledge: {new_sentence}")
                        
    def infer_safeness_or_mineness(self):
        """
        Based on new provided knowledge, updates all sentencess and mark the safe
        and mine cells of them. (if possible)

        Returns
        -------
        None.

        """
        for sentence in self.knowledge:
            known_safes = sentence.known_safes()
            if not len(known_safes) == 0: # if it is not an empty set
                print(f"known safes: {known_safes}")
                for cell in known_safes:
                    self.mark_safe(cell)
                    
            known_mines = sentence.known_mines()
            if not len(known_mines) == 0: # if it is not an empty set
                print(f"known mines: {known_mines}")
                for cell in known_mines:
                    self.mark_mine(cell)
        
        
    def get_neighbors(self, cell):
        """
        Returns neighbors of a given cell which are not mines nor safes.
        
        Parameters
        ----------
        cell : TUPLE
            DESCRIPTION.

        Returns
        -------
        neighbors : SET
            DESCRIPTION.

        """
        neighbors = set()
        i, j = cell
        for a in range(i-1, i+2):
            for b in range(j-1, j+2):
                if 0 <= a < self.height and 0 <= b < self.width:
                    candidate_neighbor = (a, b)
                    if not candidate_neighbor in self.safes and not candidate_neighbor in self.mines:
                        neighbors.add(candidate_neighbor)
        return neighbors

    def make_safe_move(self):
        """
        Returns a safe cell to choose on the Minesweeper board.
        The move must be known to be safe, and not already a move
        that has been made.

        This function may use the knowledge in self.mines, self.safes
        and self.moves_made, but should not modify any of those values.
        """
        if len(self.safes) == 0:
            return None #No known safe move is available
        else:
            for safe_move in self.safes:
                if not safe_move in self.moves_made:
                    return safe_move #Return a safe move which has not been made before
            return None #There were safe moves but all of them have been made before

    def make_random_move(self):
        """
        Returns a move to make on the Minesweeper board.
        Should choose randomly among cells that:
            1) have not already been chosen, and
            2) are not known to be mines
        """
        # for i in range(self.height):
        #     for j in range(self.width):
        #         if (i, j) not in self.moves_made and (i, j) not in self.mines:
        #             return (i, j)
        # return None
        height = self.height
        width = self.width
        if len(self.safes) + len(self.mines) == height * width:
            return None
        else:
            while True:
                i = random.randrange(height)
                j = random.randrange(width)
                if not (i, j) in self.moves_made and not (i, j) in self.mines:
                    return (i, j)