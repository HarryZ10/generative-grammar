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

    def _process_file(self, file) -> None:
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
        while not (line := file.readline().strip()).startswith("}"):
            if line.endswith(";"):
                # remove the last character (semicolon) and split the line into individual productions
                for prod in line[:-1].split(";"):
                    # strip whitespace from the production
                    prod = prod.strip()
                    if prod:
                        productions.append(prod)
            else:
                productions.append(line)

        return productions

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
        return text.replace(" ,", ",").replace(" .", ".").replace(" :", ":")

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
                stack.extend(reversed(content))
            else:
                # only append terminal symbols
                res.append(curr_symbol)

        return self._minimize_text(" ".join(res))


if __name__ == "__main__":
    rtg = RandomTextGenerator(sys.argv[1])
    print(rtg.run())
