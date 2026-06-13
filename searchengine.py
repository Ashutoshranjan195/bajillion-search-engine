"""
Bajillion Search Engine
========================
A complete implementation of the Stanford CS106A "Bajillion" search
engine assignment: builds an inverted index from a folder of .txt news
articles, then lets the user run keyword (Boolean AND) searches over
each article's title and body.

EXPECTED FILE FORMAT (one .txt file per article)
-------------------------------------------------
    line 1: source URL                  -> ignored
    line 2: article title               -> indexed
    line 3: blank separator line        -> ignored
    line 4 onward: article body text    -> indexed

USAGE
-----
    python searchengine.py <folder_name>          # print the full index
    python searchengine.py <folder_name> -s       # interactive search mode

EXAMPLES
--------
    python searchengine.py bbcnews
    python searchengine.py bbcnews -s
"""

import os
import sys
import string

from common_elements import common


# A translation table that maps every punctuation character to None,
# so str.translate() removes punctuation entirely (not just from the
# edges of a word). Built once, at import time, so it isn't rebuilt
# on every call to clean_word().
PUNCTUATION_TABLE = str.maketrans("", "", string.punctuation)


def clean_word(word):
    """
    Normalize a single token so it can be used as an index key or
    compared against an index key:
      - convert to lowercase
      - remove ALL punctuation characters anywhere in the word

    This same function is used both when BUILDING the index and when
    CLEANING the user's search query, which guarantees that a query
    like "Stanford!" matches an indexed word "stanford".

    >>> clean_word("Stanford")
    'stanford'
    >>> clean_word("bike!")
    'bike'
    >>> clean_word("U.S.A.")
    'usa'
    >>> clean_word("--")
    ''
    """
    word = word.lower()
    word = word.translate(PUNCTUATION_TABLE)
    return word


def add_words_to_index(text, filename, index):
    """
    Split `text` into whitespace-separated tokens, clean each one with
    clean_word(), and record that `filename` contains that word.

    `index` maps word -> set of filenames. A set is used here so that
    a word appearing many times in one file still only adds that
    filename once. The sets are converted to sorted lists afterwards,
    in create_index(), to match the "word -> list of filenames" spec.
    """
    for raw_word in text.split():
        word = clean_word(raw_word)
        if word == "":
            continue  # skip tokens that were pure punctuation, e.g. "--"

        if word not in index:
            index[word] = set()
        index[word].add(filename)


def create_index(folder_name):
    """
    Build the inverted index for every .txt file in `folder_name`.

    Returns:
        index  -- dict mapping each word -> sorted list of filenames
                  whose title or body contains that word
        titles -- dict mapping each filename -> that article's title
                  (used later so we can display titles in results)

    Files that are missing, too short, or unreadable as text are
    skipped rather than crashing the program, so one malformed file
    in the folder can't bring the whole search engine down.
    """
    index = {}
    titles = {}

    # sorted() gives a deterministic processing order, which makes the
    # program's behaviour repeatable/testable across runs and machines.
    for filename in sorted(os.listdir(folder_name)):
        filepath = os.path.join(folder_name, filename)

        # Only look at regular .txt files; skip sub-folders, hidden
        # files, or anything with a different extension.
        if not filename.endswith(".txt") or not os.path.isfile(filepath):
            continue

        try:
            with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
                lines = f.readlines()
        except OSError:
            # If the file can't be opened for some reason, skip it
            # instead of letting the whole indexing process crash.
            continue

        # A valid article needs at least 4 lines (URL, title, blank,
        # body). Skip anything shorter so it can't crash the program.
        if len(lines) < 4:
            continue

        # Line 2 (index 1) is the title.
        title = lines[1].strip()
        titles[filename] = title if title else "(untitled)"

        # Index every word in the title...
        add_words_to_index(title, filename, index)

        # ...and every word in the body, which starts on line 4
        # (index 3) and runs to the end of the file.
        body = "".join(lines[3:])
        add_words_to_index(body, filename, index)

    # Convert each set of filenames into a sorted list so the rest of
    # the program (and anyone inspecting `index`) sees plain lists.
    for word in index:
        index[word] = sorted(index[word])

    return index, titles


def print_index(index):
    """
    Print the entire inverted index in a readable, deterministic
    format: one word per line, sorted alphabetically, followed by the
    sorted list of filenames that contain it.

        bike: article1.txt, article3.txt
        stanford: article1.txt, article2.txt
    """
    if not index:
        print("(The index is empty -- no .txt files were found.)")
        return

    for word in sorted(index):
        files = ", ".join(index[word])
        print(f"{word}: {files}")


def search(index, query):
    """
    Look up `query` in `index` and return the SORTED list of filenames
    that contain EVERY word in the query -- a Boolean AND search.

    A query like "stanford bike" will only match files whose title or
    body contains BOTH "stanford" AND "bike" somewhere. The query is
    cleaned with the exact same clean_word() function used when
    building the index, so it is fully case- and punctuation-insensitive
    (e.g. "Stanford!" matches the same files as "stanford").

    Returns an empty list if:
      - the query (after cleaning) has no words at all, or
      - any word in the query does not appear in the index
        (since then no file could possibly satisfy the AND).
    """
    # Clean every word in the query, then drop any that became empty
    # (e.g. a query of just "!" or "--").
    query_words = [clean_word(w) for w in query.split()]
    query_words = [w for w in query_words if w != ""]

    if not query_words:
        return []

    # Start with the list of files containing the first query word.
    first_word = query_words[0]
    if first_word not in index:
        return []
    matches = index[first_word]

    # Repeatedly narrow down `matches` to only the files that ALSO
    # contain each remaining query word, using the common() helper
    # for Boolean AND.
    for word in query_words[1:]:
        if word not in index:
            return []  # word appears nowhere -> AND can never match
        matches = common(matches, index[word])

    return sorted(matches)


def display_results(filenames, titles):
    """
    Print search results in ranked order:
        1. <title> (<filename>)
        2. <title> (<filename>)
        ...
    or print "No results match that query." if `filenames` is empty.
    """
    if not filenames:
        print("No results match that query.")
        return

    for rank, filename in enumerate(filenames, start=1):
        title = titles.get(filename, "(untitled)")
        print(f"{rank}. {title} ({filename})")


def run_search_loop(index, titles):
    """
    Repeatedly prompt the user for a search query and print the
    matching results. Stops as soon as the user enters an empty (or
    whitespace-only) query -- just pressing Enter.
    """
    while True:
        query = input("Enter a query (press Enter to quit): ")

        # An empty (or all-whitespace) query ends the program.
        if query.strip() == "":
            print("Thanks for using Bajillion Search Engine!")
            break

        results = search(index, query)
        display_results(results, titles)
        print()  # blank line between searches, for readability


def main(folder_name, interactive):
    """
    Build the inverted index from `folder_name`, report how much was
    indexed, then either:
      - print the full inverted index (default mode), or
      - start the interactive search loop (if `interactive` is True).
    """
    print(f"Indexing files in '{folder_name}'...")
    index, titles = create_index(folder_name)
    print(f"Indexed {len(titles)} file(s) and {len(index)} unique word(s).\n")

    if interactive:
        run_search_loop(index, titles)
    else:
        print_index(index)


if __name__ == "__main__":
    # Expect one required argument (the folder) and an optional "-s"
    # flag to switch to interactive search mode:
    #   python searchengine.py bbcnews        -> print full index
    #   python searchengine.py bbcnews -s     -> interactive search
    args = sys.argv[1:]

    if len(args) not in (1, 2) or (len(args) == 2 and args[1] != "-s"):
        print("Usage: python searchengine.py <folder_name> [-s]")
        sys.exit(1)

    folder_arg = args[0]
    interactive_mode = "-s" in args

    if not os.path.isdir(folder_arg):
        print(f"Error: '{folder_arg}' is not a valid folder.")
        sys.exit(1)

    main(folder_arg, interactive_mode)
