import random
import sys
import os
from typing import Dict, List
import re


class RandomTextGeneratorError(Exception):
    """Base exception for RandomTextGenerator."""


class GrammarFileError(RandomTextGeneratorError):
    """Raised when there's an issue with the grammar file."""


class RandomTextGenerator:

    def __init__(self, grammar_file):

        # the file path to read from
        self.grammar_file: str = grammar_file

        # storing grammar rules in a dictionary
        self.grammar_rules: Dict[str, List[str]] = {}

        # entry non-terminal symbol
        self.start_symbol: str = None

        # program entrypoint on object instantiation
        self._read_grammar_rules()

    @staticmethod
    def _minimize_text(text: str) -> str:
        # replace spaces before special characters and handle newlines
        minimized_text = re.sub(r'\s([,!?.:\n])', r'\1', text)
        minimized_text = re.sub(r'\\n ', '\n', minimized_text)
        return minimized_text

    def _read_grammar_rules(self) -> None:
        """
        Reads grammar rules from a specified file. This method attempts
        to read grammar rules from the file specified by `grammar_file`.

        Raises:
            GrammarFileError: If the file is empty, cannot be decoded using UTF-8,
                              or does not exist.
        """
        # Check if the file size is 0 (i.e., the file is empty)
        empty = os.stat(self.grammar_file).st_size == 0
        if empty:
            raise GrammarFileError("File is empty")

        # Attempt to read the file with UTF-8 encoding
        with open(self.grammar_file, 'r', encoding='UTF-8') as file:
            self._process_file(file)

    def _process_file(self, file) -> None:
        """
        Processes the given file to extract grammar rules. This method reads
        the file line by line and expects the grammar rules to be formatted
        in a specific way.

        Each rule starts with a '{' on its own line, followed by the non-terminal
        symbol on the next line. The subsequent lines contain the productions
        for that non-terminal until a '}' is encountered.

        The method also populates the `grammar_rules` dictionar
        with the non-terminal as the key and its
        corresponding productions as the value.

        Example file format:
            {
            <non_terminal>
            <production> ;
            }

        Raises:
            GrammarFileError: If there's any inconsistency or error in the file's
                            formatting
        Args:
            file (TextIO): The file object to be processed
        """
        for line in file:
            line = line.strip()

            if line == "{":
                # Initialize the start symbol to the current non-terminal.
                # The non-terminal is expected to be on the next line
                non_terminal: str = self._validate_start_symbol(file)

                # Collect all productions, reading the subsequent lines until
                # a "}" is found
                productions: List[str] = self._consume_set_of_productions(file)

                if non_terminal:
                    # Add the non-terminal and its productions to the grammar
                    # rules dict
                    self.grammar_rules[non_terminal] = productions
                else:
                    raise GrammarFileError("Start symbol improperly formatted")
            elif line == "}":
                raise GrammarFileError(
                    "Error: Unexpected '}' bracket found outside a production set")
            else:
                if line.startswith("{"):
                    raise GrammarFileError(
                        "Error: Opening bracket '{' not formatted.")

    def _validate_start_symbol(self, file) -> str:
        """
        Validates and extracts the start symbol (non-terminal) from the given file

        Raises:
            GrammarFileError: If non-terminal symbol is not properly formed
        Args:
            file (TextIO): The file object from which the non-terminal is to be read
        Returns:
            str: The extracted non-terminal symbol
        """
        non_terminal: str = file.readline().strip()
        if self.start_symbol is None:
            # set the start symbol to init
            # trickling down grammar rules later on
            if non_terminal and non_terminal != '':
                if non_terminal.endswith(">") and non_terminal.startswith("<"):
                    self.start_symbol = non_terminal
                else:
                    raise GrammarFileError("Start symbol improperly formed")
        return non_terminal

    def _consume_set_of_productions(self, file) -> List[str]:
        """
        Extracts and processes a set of productions from the given file.

        Raises:
            GrammarFileError: If there's any inconsistency or error in the file's
                            formatting, such as missing semicolons, unexpected
                            curly braces, or improperly formatted productions
        Args:
            file (TextIO): The file object from which the productions are to be read
        Returns:
            List[str]: A list of extracted productions
        """
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
                    raise GrammarFileError(
                        "Error: '}' found but improperly formatted.")

                elif line.endswith("}"):
                    removed_braces = line[:-1].strip()
                    if removed_braces.endswith(";"):
                        # remove the last character (semicolon)
                        # and split the line into solo productions
                        self._add_productions_from_line(
                            removed_braces[:-1], productions)
                    else:
                        raise GrammarFileError(
                            "Error: Improperly formatted semicolons")
                else:
                    raise GrammarFileError(
                        "Error: Improperly formatted semicolons or curly braces, or no rules")

                return productions

        # if we are, it means we did not find a "}" mark
        raise GrammarFileError("File corrupt EOF: No matching '}' found!  ")

    def _add_productions_from_line(
            self, raw_line: str, productions: List[str]) -> None:
        """
        Processes a raw line containing multiple productions and adds them to the provided list.

        Args:
            - raw_line (str): The raw line containing one or more productions separated by semicolons
            - productions List[str]: The list to which the processed productions will be appended
         """
        multiple_prods = raw_line.split(";")
        for prod in multiple_prods:
            productions.append(prod.strip())

    def _get_content(self, non_terminal) -> List[str]:
        """
        Retrieves a random production rule associated with the given non-terminal symbol

        Args:
            non_terminal (str): The non-terminal symbol
        Returns:
            List[str]: A list of symbols (both terminal and non-terminal) from the randomly
                        selected production rule.
        """
        # retrieve the list of production rules associated with the given
        # non-terminal symbol
        productions: List[str] = self.grammar_rules.get(non_terminal, [])

        # if there any any productions
        if productions:

            # then get a random one of them
            production: str = random.choice(productions)

            # Lookbehind assertion: (?<=>) matches if word followed by '>'
            # Lookahead assertion:  (?=<) matches if '<' is followed by a word
            # We're combining this with the string potential with multiple non-terminals,
            # to split on each symbol non-terminal or terminal into a list
            symbols: List[str] = re.split(r'(?<=>)|(?=<)', production)

            # return non-whitespace symbols
            return [symbol.strip() for symbol in symbols if symbol.strip()]
        return []

    def run(self) -> str:
        # initialize stack with entry symbol and output
        stack, res = [self.start_symbol], []
        while stack:
            # stack gets consumed to replace all non-terminal symbols
            curr_symbol: str = stack.pop()

            # if current symbol is non-terinal, replace with a terminal symbol
            if curr_symbol in self.grammar_rules:

                # replace non-terminal with new randomly selected terminal
                # symbols
                content: List[str] = self._get_content(curr_symbol)

                # the content can be empty '' because a rule can just end with ";"
                # without words preceding to denote an empty option
                if content is not None:
                    stack.extend(reversed(content))
                else:
                    raise RandomTextGeneratorError(
                        f"No productions found for {curr_symbol}")
            else:
                # Before we build output, we check if it has
                # the angle brackets
                if not re.match(r'^<.*>$', curr_symbol):
                    res.append(curr_symbol)
                else:
                    raise RandomTextGeneratorError(
                        f"Error: No productions found for {curr_symbol}")

        return self._minimize_text(" ".join(res))


if __name__ == "__main__":

    try:
        # File must exist
        if len(sys.argv) > 1:
            rtg = RandomTextGenerator(sys.argv[1])
            print(rtg.run())
        else:
            raise GrammarFileError("No file provided")

    except UnicodeDecodeError:
        print("Cannot read file encoding. Use default UTF-8.")
        sys.exit(1)

    except FileNotFoundError:
        # Handle cases where the file does not exist
        print("File does not exist.")
        sys.exit(1)

    except RandomTextGeneratorError as e:
        print(e)
        sys.exit(1)
