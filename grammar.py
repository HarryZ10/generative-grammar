import random
import sys
from typing import Dict

class RandomTextGenerator:

    def __init__(self, grammar_file):

        self.grammar_file: str = grammar_file       # the file path to read from
        self.grammar_rules: Dict[str, list] = {}    # store grammar rules in a map 
        self.start_symbol: str = None               # entry non-terminal symbol

        self._read_grammar_rules()                  # entrypoint to the program

    def _read_grammar_rules(self) -> None:
        try:
            with open(self.grammar_file, 'r', encoding='UTF-8') as file:
                self._process_file(file)
        except UnicodeDecodeError:
            with open(self.grammar_file, 'r', encoding='ISO-8859-1') as file:
                self._process_file(file)
        except FileNotFoundError:
            print("File not found")
            sys.exit(1)

    def _process_file(self, file) -> None:
        for line in file:
            # get current line content
            line = line.strip()

            # a new production set starts with a "{"
            if line.startswith("{"):

                # initialize start symbol to the current non-terminal
                # non-terminal is on the next line
                non_terminal: str = self._init_start_symbol(file)
                # collect all productions consuming the rest of the lines until "}" is found
                productions: list = self._consume_set_of_productions(file) 

                # add the non-terminal and its productions to the grammar rules dict
                self.grammar_rules[non_terminal] = productions

    def _init_start_symbol(self, file) -> str:
        non_terminal: str = file.readline().strip()
        if self.start_symbol is None:
            # set the start symbol to init
            # trickling down grammar rules later on
            self.start_symbol = non_terminal
        return non_terminal

    def _consume_set_of_productions(self, file) -> list:
        productions: list = [] 

        # going through each line in the remaining
        # production set, we strip each line
        for line in file:
            line: str = line.strip()

            # a production must end with a ";"
            if line.endswith(";"):
                # remove the last character (semicolon)
                # and split the line into solo productions
                multiple_prods = line[:-1].split(";")
                for prod in multiple_prods:
                    if prod:
                        productions.append(prod.strip())

            # once we find the `}` we can just return
            # the found productions
            elif line.startswith("}"):
                return productions

        # if we are, it means we did not find a "}" mark
        print("File corrupt EOF: No matching '}' found!  ")
        sys.exit(1)

    def _get_content(self, non_terminal) -> list:
        # retrieve the list of production rules associated with the given non-terminal symbol
        productions: list = self.grammar_rules.get(non_terminal, [])
        if productions:
            production, symbols, symbol = random.choice(productions), [], ""

            for char in production:
                # "<" starting character for non-terminal symbol
                if char == '<':
                    # if there is any text built up in the symbol variable,
                    # strip whitespace from its ends and add it to the symbols list
                    if symbol.strip():
                        symbols.append(symbol.strip())
                    # start building a new symbol starting with '<'
                    symbol = '<'

                # ">" starting character for non-terminal symbol
                elif char == '>':
                    symbol += '>'
                    symbols.append(symbol)
                    symbol = ""

                # build the symbol inside the <> or using other punctuation
                else:
                    # add the character to the current symbol
                    symbol += char

            if symbol:
                symbols.append(symbol.strip())

            return symbols
        else:
            return None

    def _minimize_text(self, text: str) -> str:
        return text.replace(" ,", ",") \
                   .replace(" .", ".") \
                   .replace(" :", ":") \
                   .replace(" \\n ", "\n")

    def run(self) -> str:
        # initialize stack with entry symbol and output
        stack, res = [self.start_symbol], []

        while stack:
            # stack gets consumed to replace all non-terminal symbols
            curr_symbol: str = stack.pop()

            # if current symbol is non-terinal, replace with a terminal symbol
            if curr_symbol in self.grammar_rules:
                # replace non-terminal with new randomly selected terminal symbols
                content: list = self._get_content(curr_symbol)
                if content:
                    stack.extend(reversed(content))
                else:
                   print("No productions found for", curr_symbol)
                   sys.exit(1)
            else:
                # only append terminal symbols
                res.append(curr_symbol)

        return self._minimize_text(" ".join(res))


if __name__ == "__main__":
    rtg = RandomTextGenerator(sys.argv[1])
    print(rtg.run())
