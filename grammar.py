import random
import sys

class RandomTextGenerator:

    def __init__(self, grammar_file):

        self.grammar_file = grammar_file            # the file to read from
        self.grammar_rules: dict = {}               # store grammar rules in a map 
        self.start_symbol: str = None               # entry non-terminal symbol

        self.read_grammar()                         # entrypoint to the program

    def read_grammar(self) -> None:
        with open(self.grammar_file, 'r') as file:
            eof: bool = False
            while not eof:
                line = file.readline()
                if not line:
                    eof = True  # stop processig productions
                else:
                    line = line.strip() # continue processing production without whitespace

                    # production set starts with a "{"
                    if line.startswith("{"):

                        non_terminal: str = file.readline().strip() # non-terminal is on the next line

                        # initialize start symbol to the current non-terminal
                        if self.start_symbol is None:
                            self.start_symbol = non_terminal

                        productions: list = []

                        # read the productions until "}" is found
                        while not (line := file.readline().strip()).startswith("}"):

                            if line.endswith(";"):
                                line = line[:-1] # removes trailing semicolon if it exists

                            productions.append(line) # add line to productions

                        # add the non-terminal and its productions to the grammar rules dict
                        self.grammar_rules[non_terminal] = productions

    def get_random_production(self, non_terminal) -> str:
        productions: list = self.grammar_rules.get(non_terminal, [])
        return random.choice(productions) if productions else None

    def generate_text(self) -> str:
        # initialize stack with entry symbol and output
        stack, output = [self.start_symbol], []

        while stack:
            # pop the last element to get a current symbol
            current_symbol = stack.pop()

            # now we check if it's in our dictionary of rules
            if current_symbol in self.grammar_rules:

                # get a random production (or terminal symbol) and maintain in-stack order
                production = self.get_random_production(current_symbol)
                production_symbols = production.split()[::-1]

                # Push each symbol from the production to replace non-terminals
                stack.extend(production_symbols)
            else:
                # if the current symbol is a terminal
                output.append(current_symbol)

        return ' '.join(output)

def main(arg):
    generator = RandomTextGenerator(arg)
    print(generator.generate_text())

if __name__ == "__main__":
    main(sys.argv[1])
