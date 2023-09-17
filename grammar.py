import random
import sys

class RandomTextGenerator:

    def __init__(self, grammar_file):
        self.grammar_file: str = grammar_file       # the file path to read from
        self.grammar_rules: dict = {}               # store grammar rules in a map 
        self.start_symbol: str = None               # entry non-terminal symbol
        self._read_grammar_rules()                  # entrypoint to the program

    def _read_grammar_rules(self) -> None:
        with open(self.grammar_file, 'r') as file:
            eof: bool = False
            while not eof:
                line = file.readline()
                if not line:
                    # stop processing productions
                    eof = True
                else:
                    # process productions without whitespace
                    line = line.strip()

                    # a production set starts with a "{"
                    if line.startswith("{"):
                        # initialize start symbol to the current non-terminal
                        # non-terminal is on the next line
                        non_terminal: str = file.readline().strip()

                        if self.start_symbol is None:
                            self.start_symbol = non_terminal

                        # collect all productions consuming the rest of the lines until "}" is found
                        productions: list = [] 
                        while not (line := file.readline().strip()).startswith("}"):
                            # add production without ';'
                            productions.append(line[:-1]) 

                        # add the non-terminal and its productions to the grammar rules dict
                        self.grammar_rules[non_terminal] = productions

    def _get_content(self, non_terminal) -> str:
        productions: list = self.grammar_rules.get(non_terminal, [])
        return random.choice(productions) if productions else None

    def run(self) -> str:
        # initialize stack with entry symbol and output
        stack, res = [self.start_symbol], []

        while stack:
            # stack gets consumed to replace all non-terminal symbols
            curr_symbol = stack.pop()

            # if current symbol is non-terinal, replace with a terminal symbol
            if curr_symbol in self.grammar_rules:
                # replace non-terminal with new randomly selected terminal symbols
                content = self._get_content(curr_symbol)
                stack.extend(content.split()[::-1]) 
            else:
                # only append terminal symbols
                res.append(curr_symbol)

        return " ".join(res)

if __name__ == "__main__":
    rtg = RandomTextGenerator(sys.argv[1])
    print(rtg.run())
