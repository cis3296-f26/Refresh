import asyncio

from app.deck_actions import parse_deck


# Stand-in for an uploaded file: parse_deck only needs an async text() method
class FakeUpload:
    def __init__(self, content):
        self.content = content

    async def text(self):
        return self.content


# Run the async parse_deck on a string and return the parsed cards
def parse(content):
    return asyncio.run(parse_deck(FakeUpload(content)))


# A pipe separates question and answer
def test_pipe_delimiter():
    assert parse("What is 2+2? | 4") == [{"question": "What is 2+2?", "answer": "4"}]


# Every other supported delimiter works the same way
def test_other_delimiters():
    for line in ["Q ; A", "Q : A", "Q , A", "Q :: A", "Q\tA"]:
        assert parse(line) == [{"question": "Q", "answer": "A"}]


# Lines starting with # and blank lines are ignored
def test_skips_comments_and_blank_lines():
    assert parse("# title\n\nQ | A\n") == [{"question": "Q", "answer": "A"}]


# A line with no delimiter can't be a card, so it's ignored
def test_skips_lines_without_delimiter():
    assert parse("just some text") == []


# Both sides are required: an empty question or answer is ignored
def test_skips_empty_question_or_answer():
    assert parse("| answer only\nquestion only |") == []


# An empty file produces no cards
def test_empty_file():
    assert parse("") == []


# The bundled example file should parse into its 3 cards
def test_example_deck_has_three_cards():
    with open("example/example_deck.txt") as f:
        assert len(parse(f.read())) == 3
