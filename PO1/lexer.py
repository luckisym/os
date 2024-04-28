#!/usr/bin/env python3
# # # # # # # # # # # # # # # # # # # # # # # # # # # # #
#  Framework for Automaten en Formele Talen             #
#  Written by: Robin Visser & Tristan Laan              #
#  based on work by: Bas van den Heuvel & Daan de Graaf #
#                                                       #
#  This work is licensed under a Creative Commons       #
#  “Attribution-ShareAlike 4.0 International”  license. #
# # # # # # # # # # # # # # # # # # # # # # # # # # # # #

# Can probably be removed next year, but just to make sure for now,
# since the error is not very clear on Python 3.9.
import sys
if sys.version_info < (3, 10):
    print("FA.py requires Python 3.10 or newer. Cannot continue...")
    sys.exit(1)

from FA import FA, FAError
from pathlib import Path
import string


def create_fa(verbose: bool = False) -> FA:
    """
    Creates the finite automaton (FA) for trace tokenization
    Characters for left endmarker and BLANK: ⊢ , ⊔
    """

    Q = ['START', 'SPACE', 'MLEFT', 'MRIGHT', 'READ', 'WRITE', 'BLANK', 'LEM',
         'SYMBOL']
    Sigma = [' ', '<', '>', '-', '+', '⊔', '⊢', 'character', 'digit']
    delta = {'START': {' ': 'SPACE',
                       '<': 'MLEFT',
                       'character': 'SYMBOL',
                       '>': 'MRIGHT',
                       '-': 'READ',
                       '+': 'WRITE',
                       '⊔': 'BLANK',
                       '⊢': 'LEM',
                       'digit': 'SYMBOL'
                       },
             'SYMBOL': {'character': 'SYMBOL',
                        'digit': 'SYMBOL'}}

    s = 'START'
    F = ['SPACE', 'MLEFT', 'MRIGHT', 'READ', 'WRITE', 'BLANK', 'LEM', 'SYMBOL']

    M = FA(Q, Sigma, delta, s, F, verbose)

    return M


def char_type(char: str) -> str:
    """
    Returns the type of a character found in the trace
    """
    if char in string.digits:
        return 'digit'
    elif char in string.ascii_letters:
        return 'character'
    else:
        return char


def lexer(fa: FA, trace: str) -> list[tuple[str, str]]:
    """
    The lexer iterates through the trace, tokenizing and assigning states to it
    fa: The finite automaton
    trace: A single string
    returns: A list of tuples containing first the token then the state.
    If something goes wrong the function should raise an FAError exception.
    E.g. raise FAError("Error message").
    """

    # EXPLANATION
    # This function breaks down an input trace into tokens using a
    # finite automaton. It groups consecutive symbol characters to form
    # symbol tokens. As it goes through the trace, it gathers symbol
    # characters until it reaches a new state. Then, it adds the gathered
    # symbol token and the state to the output list. This method ensures
    # that symbol sequences are recognized and handled as separate tokens.
    # The output list contains pairs of tokens and states,
    # representing the tokenization of the input trace.

    fa.reset()

    transitions = []
    symbol_buffer = ""

    for token in trace:
        if not fa.transition(char_type(token)):
            raise FAError(f"State '{fa.current_state.name}' has no "
                          f"transition for token '{token}'")

        if fa.current_state.name == 'SYMBOL':
            if not symbol_buffer:
                symbol_buffer = token
            else:
                symbol_buffer += token
        else:
            if symbol_buffer:
                transitions.append((symbol_buffer, "SYMBOL"))
                symbol_buffer = ""

            transitions.append((token, fa.current_state.name))

        fa.reset()

    if symbol_buffer:
        transitions.append((symbol_buffer, "SYMBOL"))

    return transitions


def main(file: Path, verbose: bool = False) -> None:
    """
    Reads multiple traces from the file at 'file' and feeds them one by one to
    the lexer.
    """
    M = create_fa(verbose)

    with file.open(encoding='utf-8') as f:
        traces = [line.rstrip('\n') for line in f]

    for trace in traces:
        M.reset()
        print(f"Trace : \"{trace}\"")
        lexed_trace = lexer(M, trace)
        print(f"Lexer : {lexed_trace}")


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description='Tokenize a TM trace')
    parser.add_argument('-v', '--verbose', action='store_true',
                        help='enable verbose mode of FA')
    parser.add_argument('tracefile', type=Path,
                        help='file containing traces to tokenize')
    args = parser.parse_args()
    main(args.tracefile, args.verbose)
