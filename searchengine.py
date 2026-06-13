"""
File: searchengine.py
---------------------
CS106A Assignment 6: Bajillion Search Engine

This program implements a simple search engine that builds
an inverted index from a collection of text files and allows
the user to perform Boolean AND queries across those documents.

Usage:
    python searchengine.py <directory>          Build and print the index.
    python searchengine.py <directory> -s       Build index and enter search mode.

The program reads all .txt files from the specified directory,
builds an inverted index mapping terms to the files that contain
them, and optionally provides an interactive search interface.
"""

import os
import sys
import string

from common_elements import common


def textfiles_in_dir(dirname):
    """
    Returns a list of full file paths for all .txt files
    found in the given directory.

    Parameters:
        dirname (str): Path to the directory to scan.

    Returns:
        list: Sorted list of absolute paths to .txt files.
    """
    filenames = []
    for filename in os.listdir(dirname):
        if filename.endswith('.txt'):
            # Build the full path so files can be opened later
            full_path = os.path.join(dirname, filename)
            filenames.append(full_path)
    filenames.sort()  # Sort for consistent ordering
    return filenames


def create_index(filenames, index, file_titles):
    """
    Builds an inverted index from a list of text files.

    For each file:
      - The first line is treated as the document title
        and stored in file_titles[filename].
      - The remaining lines are split into terms (by whitespace).
      - Each term is cleaned: leading/trailing punctuation is
        stripped and the term is lowercased.
      - Empty terms (after stripping) are ignored.
      - The inverted index maps each term to a list of filenames
        containing that term (no duplicate filenames per term).

    Parameters:
        filenames (list): List of file paths to process.
        index (dict): The inverted index dict to populate.
                      key = term (str), value = list of filenames.
        file_titles (dict): Dict to populate with file titles.
                            key = filename (str), value = title (str).
    """
    for filename in filenames:
        with open(filename, 'r', encoding='utf-8', errors='ignore') as f:
            lines = f.readlines()

        if len(lines) == 0:
            continue  # Skip empty files

        # First line is the title (strip trailing whitespace/newline)
        title = lines[0].strip()
        file_titles[filename] = title

        # Process the remaining lines for index terms
        # Track which terms we've already added for this file
        # to avoid duplicate filename entries in the index
        terms_seen_in_file = set()

        for line in lines[1:]:
            # Split each line into whitespace-separated tokens
            words = line.split()
            for word in words:
                # Strip punctuation from beginning and end
                term = word.strip(string.punctuation)
                # Lowercase the term
                term = term.lower()

                # Skip terms that became empty after stripping
                if term == '':
                    continue

                # Add the term to the index if not already present
                if term not in index:
                    index[term] = []

                # Only add filename once per term per file
                if term not in terms_seen_in_file:
                    index[term].append(filename)
                    terms_seen_in_file.add(term)


def search(index, query):
    """
    Searches the inverted index for documents matching ALL
    terms in the query (Boolean AND).

    The query string is split into individual terms. For each
    term, the list of matching filenames is retrieved from the
    index. The results are intersected across all terms using
    the common() function from common_elements.py.

    Parameters:
        index (dict): The inverted index (term -> list of filenames).
        query (str): The search query (lowercase, no punctuation).
                     Multiple terms are space-separated.

    Returns:
        list: Filenames that contain ALL query terms.
              Returns an empty list if any term is not in the index.
    """
    terms = query.split()

    if len(terms) == 0:
        return []

    # Start with the results for the first term
    first_term = terms[0]
    if first_term not in index:
        return []  # If first term isn't indexed, no results possible
    result = list(index[first_term])  # Copy the list to avoid mutation

    # Intersect with results for each subsequent term
    for term in terms[1:]:
        if term not in index:
            return []  # Term not found, so AND intersection is empty
        result = common(result, index[term])

    return result


def do_search(index, file_titles):
    """
    Runs the interactive search loop.

    Repeatedly prompts the user for a search query,
    performs the search, and displays the results with
    document titles and filenames. An empty query exits.

    Parameters:
        index (dict): The inverted index.
        file_titles (dict): Dict mapping filenames to titles.
    """
    while True:
        query = input("Query (empty to quit): ")

        # Exit on empty query
        if query == '':
            break

        # Perform the search
        results = search(index, query)

        # Display results
        if len(results) == 0:
            print("No results match that query.")
        else:
            print(f"Found {len(results)} result(s):")
            for filename in results:
                title = file_titles.get(filename, "(no title)")
                print(f"  {title} ({filename})")

        print()  # Blank line between queries for readability


def main():
    """
    Main entry point for the Bajillion Search Engine.

    Handles command-line arguments:
      - First argument: directory containing .txt files.
      - Optional '-s' flag: enter interactive search mode
        after building the index.

    Without -s, the program builds and prints the inverted index.
    With -s, the program builds the index and starts a search loop.
    """
    # Validate command-line arguments
    if len(sys.argv) < 2:
        print("Usage: python searchengine.py <directory> [-s]")
        print("  <directory>  Path to folder containing .txt files")
        print("  -s           Enter interactive search mode")
        return

    dirname = sys.argv[1]

    # Check if the directory exists
    if not os.path.isdir(dirname):
        print(f"Error: '{dirname}' is not a valid directory.")
        return

    # Determine if search mode is requested
    search_mode = '-s' in sys.argv

    # Get all .txt files in the directory
    filenames = textfiles_in_dir(dirname)
    if len(filenames) == 0:
        print(f"No .txt files found in '{dirname}'.")
        return

    print(f"Building index from {len(filenames)} file(s) in '{dirname}'...")

    # Build the inverted index
    index = {}
    file_titles = {}
    create_index(filenames, index, file_titles)

    print(f"Index built with {len(index)} unique term(s).")
    print()

    if search_mode:
        # Interactive search mode
        print("=== Bajillion Search Engine ===")
        print("Enter search terms (space-separated for AND queries).")
        print()
        do_search(index, file_titles)
        print("Goodbye!")
    else:
        # Print the index (useful for debugging / the non-search case)
        print("Inverted Index:")
        print("-" * 40)
        for term in sorted(index.keys()):
            print(f"  '{term}' => {index[term]}")


if __name__ == '__main__':
    main()
