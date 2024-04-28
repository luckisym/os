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

from FA import FA
from pathlib import Path
import lexer as lexer


def create_fa(verbose: bool = False) -> FA:
    """
    Creates the finite automaton (FA) for step verification
    Characters for left endmarker and BLANK: ⊢ , ⊔
    """

    Q = ['Start', 's1', 's2', 's3', 's4', 's5']
    Sigma = ['MLEFT', 'MRIGHT', 'READ', 'WRITE', 'BLANK', 'LEM', 'SYMBOL']
    delta = {'Start': {'READ': 's1'},
             's1': {'SYMBOL': 's2',
                    'LEM': 's2',
                    'BLANK': 's2'},
             's2': {'WRITE': 's3'},
             's3': {'SYMBOL': 's4',
                    'LEM': 's4',
                    'BLANK': 's4'},
             's4': {'MLEFT': 's5',
                    'MRIGHT': 's5'},
             's5': {'READ': 's1'}}

    s = 'Start'
    F = ['s5']

    M = FA(Q, Sigma, delta, s, F, verbose)

    return M


def verify_steps(fa: FA, lexed_trace: list[tuple[str, str]]) -> bool:
    """
    The verification function steps through the lexed trace and feeds the token
    portion of tuple to the fa. Either filter out SPACE tokens or adjust the FA
    fa: The finite automaton
    lexed_trace: A list of tuples of the form (event, token).
    returns: True if the trace is valid, false otherwise.
    """

    fa.reset()

    input_count = 0

    for token in lexed_trace:
        input_symbol = token[1]

        # Ignore SPACE tokens
        if input_symbol == 'SPACE':
            continue

        # Transition the FA with the input symbol
        if not fa.transition(input_symbol):
            return False

        # Increment the input count for every non-SPACE token
        input_count += 1

    # Check if the final state of the FA is reached and if the
    # input count is a multiple of 5
    if not fa.is_final() or input_count % 5 != 0:
        return False
    else:
        return True


def main(file: Path, verbose: bool = False) -> None:
    """
    Reads multiple traces from the file at 'path' and feeds them first to the
    lexer and then to verify_steps.
    """

    with file.open(encoding='utf-8') as f:
        traces = [line.rstrip('\n') for line in f]

    M_lexer = lexer.create_fa(verbose)
    M_verify = create_fa(verbose)

    for trace in traces:
        M_lexer.reset()
        M_verify.reset()
        print(f"Trace : \"{trace}\"")
        lexed_trace = lexer.lexer(M_lexer, trace)
        print(f"Lexer : {lexed_trace}")
        correct = verify_steps(M_verify, lexed_trace)
        print(f"Verify: {correct}")


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description='Tokenize a TM trace')
    parser.add_argument('-v', '--verbose', action='store_true',
                        help='enable verbose mode of FA')
    parser.add_argument('tracefile', type=Path,
                        help='file containing traces to verify')
    args = parser.parse_args()
    main(args.tracefile, args.verbose)
