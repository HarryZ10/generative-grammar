import random
import sys
from typing import Dict, List

class RandomTextGeneratorError(Exception):
    """Base exception for RandomTextGenerator."""

class GrammarFileError(RandomTextGeneratorError):
    """Raised when there's an issue with the grammar file."""

class RandomTextGenerator:

    def __init__(self, grammar_file):

        self.grammar_file: str = grammar_file            # the file path to read from
        self.grammar_rules: Dict[str, List[str]] = {}    # store grammar rules in a map
        self.start_symbol: str = None                    # entry non-terminal symbol
        self._read_grammar_rules()                       # entrypoint to the program

    @staticmethod
    def _minimize_text(text: str) -> str:
        return text.replace(" ,", ",").replace(" .", ".").replace(" :", ":").replace(" \\n ", "\n")

    def _read_grammar_rules(self) -> None:
        try:
            with open(self.grammar_file, 'r', encoding='UTF-8') as file:
                self._process_file(file)
        except UnicodeDecodeError:
            raise GrammarFileError("Cannot read file encoding. Use default UTF-8.")
        except FileNotFoundError:
            raise GrammarFileError("File does not exist.")

    def _process_file(self, file) -> None:

        for line in file:
            line = line.strip()

            if line == "{":

                # initialize start symbol to the current non-terminal
                # non-terminal is on the next line
                non_terminal: str = self._init_start_symbol(file)

                # collect all productions consuming the rest of the lines until "}" is found
                productions: List[str] = self._consume_set_of_productions(file)

                if non_terminal:
                    # add the non-terminal and its productions to the grammar rules dict
                    self.grammar_rules[non_terminal] = productions
                else:
                    raise GrammarFileError("Start symbol improperly formatted")

            elif line == "}":
                raise GrammarFileError("Error: Unexpected '}' bracket found outside a production set")
            else:
                if line.startswith("{"):
                    raise GrammarFileError("Error: Opening bracket '{' not formatted.")

    def _init_start_symbol(self, file) -> str:
        non_terminal: str = file.readline().strip()
        if self.start_symbol is None:
            # set the start symbol to init
            # trickling down grammar rules later on
            if non_terminal and non_terminal != '':

                if non_terminal.endswith(">") and non_terminal.startswith("<"):
                    # set the start symbol to init
                    # trickling down grammar rules later on
                    self.start_symbol = non_terminal
                else:
                    raise GrammarFileError("Start symbol improperly formed")

        return non_terminal

    def _consume_set_of_productions(self, file) -> List[str]:
        productions: List[str] = []

        # going through each line in the remaining productions
        for line in file:
            line = line.strip()

            # a production must end with a ";"
            if line.endswith(";"):
                # remove the last character (semicolon)
                # and split the line into solo productions
                self._add_productions_from_line(line[:-1], productions)

            # once we find the `}` we can just return
            # the found productions
            elif line == "}":
                return productions

            elif line == "{":
                raise GrammarFileError("Error: Unexpected '{' found!")
            else:
                if line.startswith("}"):
                    raise GrammarFileError("Error: '}' found but improperly formatted.")

                elif line.endswith("}"):

                    removed_braces = line[:-1].strip()
                    if removed_braces.endswith(";"):
                        # remove the last character (semicolon)
                        # and split the line into solo productions
                        self._add_productions_from_line(removed_braces, productions)

                    return productions

        # if we are, it means we did not find a "}" mark
        raise GrammarFileError("File corrupt EOF: No matching '}' found!  ")

    def _add_productions_from_line(self, line: str, productions: List[str]) -> None:
        multiple_prods = line[:-1].split(";")
        for prod in multiple_prods:
            productions.append(prod.strip())

    def _get_content(self, non_terminal) -> List[str]:
        # retrieve the list of production rules associated with the given non-terminal symbol
        productions: List[str] = self.grammar_rules.get(non_terminal, [])
        if productions:
            production, symbols, symbol = random.choice(productions), [], ""

            for char in production:
                # "<" starting character for non-terminal symbol
                if char == '<':
                    # add it to the symbols list if symbol is found
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

    def run(self) -> str:
        # initialize stack with entry symbol and output
        stack, res = [self.start_symbol], []

        while stack:
            # stack gets consumed to replace all non-terminal symbols
            curr_symbol: str = stack.pop()

            # if current symbol is non-terinal, replace with a terminal symbol
            if curr_symbol in self.grammar_rules:
                # replace non-terminal with new randomly selected terminal symbols
                content: List[str] = self._get_content(curr_symbol)

                if content is not None:
                    stack.extend(reversed(content))
                else:
                    raise RandomTextGeneratorError(f"No productions found for {curr_symbol}")
            else:
                # only append terminal symbols
                res.append(curr_symbol)

        return self._minimize_text(" ".join(res))

if __name__ == "__main__":
    try:
        rtg = RandomTextGenerator(sys.argv[1])
        print(rtg.run())
    except RandomTextGeneratorError as e:
        print(e)
        sys.exit(1)
