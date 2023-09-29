from grammar import RandomTextGenerator, RandomTextGeneratorError, GrammarFileError
import pytest


@pytest.mark.unit_test
def test_basic_grammar():
    # Create a temporary grammar file
    grammar_content = """
{
<start>
<hello> ;
}

{
<hello>
hi ;
}
"""
    with open("temp_grammar.txt", "w") as f:
        f.write(grammar_content)

    # Initialize the RandomTextGenerator with the temporary grammar file
    rtg = RandomTextGenerator("temp_grammar.txt")

    # Generate the random text
    result = rtg.run()

    # Assert the result
    assert result == "hi"


@pytest.mark.unit_test
def test_invalid_grammar():
    # Create a temporary invalid grammar file
    invalid_grammar_content = """
{
<start>
<hello> ;
}
"""
    with open("temp_invalid_grammar.txt", "w") as f:
        f.write(invalid_grammar_content)

    # Expect an error when initializing the RandomTextGenerator with the invalid grammar file
    with pytest.raises(RandomTextGeneratorError):
        rtg = RandomTextGenerator("temp_invalid_grammar.txt")
        rtg.run()


@pytest.mark.unit_test
def test_empty_grammar_file():
    # Create an empty temporary grammar file
    with open("temp_empty_grammar.txt", "w") as f:
        pass

    # Expect a GrammarFileError when initializing the RandomTextGenerator with the empty grammar file
    with pytest.raises(GrammarFileError, match="File is empty"):
        RandomTextGenerator("temp_empty_grammar.txt")


@pytest.mark.unit_test
def test_missing_closing_brace():
    # Create a temporary grammar file with missing closing brace
    grammar_content = """
{
<start>
<hello> ;
"""
    with open("temp_missing_brace_grammar.txt", "w") as f:
        f.write(grammar_content)

    # Expect a GrammarFileError when initializing the RandomTextGenerator with the invalid grammar file
    with pytest.raises(GrammarFileError, match="No matching '}' found"):
        RandomTextGenerator("temp_missing_brace_grammar.txt")


@pytest.mark.unit_test
def test_invalid_start_symbol():
    # Create a temporary grammar file with invalid start symbol
    grammar_content = """
{
start
<hello> ;
}
"""
    with open("temp_invalid_start_symbol_grammar.txt", "w") as f:
        f.write(grammar_content)

    # Expect a GrammarFileError when initializing the RandomTextGenerator with the invalid grammar file
    with pytest.raises(GrammarFileError, match="Start symbol improperly formed"):
        RandomTextGenerator("temp_invalid_start_symbol_grammar.txt")


@pytest.mark.unit_test
def test_missing_semicolon():
    # Create a temporary grammar file with missing semicolon
    grammar_content = """
{
<start>
<hello>
}
"""
    with open("temp_missing_semicolon_grammar.txt", "w") as f:
        f.write(grammar_content)

    # Expect a GrammarFileError when initializing the RandomTextGenerator with the invalid grammar file
    with pytest.raises(GrammarFileError, match="Improperly formatted semicolons"):
        RandomTextGenerator("temp_missing_semicolon_grammar.txt")


@pytest.mark.unit_test
def test_no_production_rules():
    # Create a temporary grammar file with missing semicolon
    grammar_content = """
{
<start>
}
"""
    with open("temp_no_rules_grammar.txt", "w") as f:
        f.write(grammar_content)

    # Expect a GrammarFileError when initializing the RandomTextGenerator with the invalid grammar file
    with pytest.raises(RandomTextGeneratorError):
        rtg = RandomTextGenerator("temp_no_rules_grammar.txt")
        rtg.run()


@pytest.mark.unit_test
def test_no_production_at_all():
    # Create a temporary grammar file with missing semicolon
    grammar_content = """
{
}
"""
    with open("temp_no_rules_grammar_2.txt", "w") as f:
        f.write(grammar_content)

    # Expect a GrammarFileError when initializing the RandomTextGenerator with the invalid grammar file
    with pytest.raises(GrammarFileError):
        rtg = RandomTextGenerator("temp_no_rules_grammar_2.txt")
        rtg.run()


# Clean up temporary files after tests


@pytest.mark.unit_test
def teardown_module():
    import os
    os.remove("temp_grammar.txt")
    os.remove("temp_invalid_grammar.txt")
    os.remove("temp_empty_grammar.txt")
    os.remove("temp_missing_brace_grammar.txt")
    os.remove("temp_invalid_start_symbol_grammar.txt")
    os.remove("temp_missing_semicolon_grammar.txt")
    os.remove("temp_no_rules_grammar.txt")
    os.remove("temp_no_rules_grammar_2.txt")
