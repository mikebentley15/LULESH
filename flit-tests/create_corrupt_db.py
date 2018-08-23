#!/usr/bin/env python3

import corrupt_clang

from argparse import ArgumentParser
import csv
import os
import random
import subprocess as subp
import sys
import tempfile

def parse_args(arguments):
    'Parse arguments and returned the parsed product'
    parser = ArgumentParser()
    parser.add_argument('procfiles', metavar='ProcFile', nargs='+',
                        help='''
                            The .proc files generated by the corrupt clang
                            compiler when in --capture-choices mode.  This is
                            the set of files where the random choices will be
                            made.
                            ''')
    parser.add_argument('-n', '--number', type=int, default=1000,
                        help='''
                            Number of corruption choices to make.  The default
                            is to make 1000 of them.
                            ''')
    parser.add_argument('-o', '--output', default='corruptions.sqlite',
                        help='''
                            The name of the sqlite file to use.  The default is
                            'corruptions.sqlite'.
                            ''')
    parser.add_argument('-s', '--seed', default=42,
                        help='''
                            The seed for the random number generator.  The
                            default is 42.
                            ''')
    return parser.parse_args(arguments)

def main(arguments):
    'Main logic here'
    args = parse_args(arguments)
    random.seed(args.seed)
    corrupt_clang.random.seed(args.seed)
    
    functions = corrupt_clang.parse_captured(args.procfiles)
    choices = []
    for _ in range(args.number):
        choice = corrupt_clang.choose_injection(functions)
        choices.append(
            '{x.fname},{x.func},{x.instr},{x.val},{x.op}'.format(x=choice))

    # create the CSV file containing the results to use
    with tempfile.NamedTemporaryFile(suffix='.csv', mode='w') as fout:
        writer = csv.writer(fout)
        # header row
        writer.writerow([
            'name',
            'host',
            'compiler',
            'optl',
            'switches',
            'precision',
            'score_hex',
            'score',
            'resultfile',
            'comparison_hex',
            'comparison',
            'file',
            'nanosec',
            ])
        for i, choice in enumerate(choices):
            writer.writerow([
                'Lulesh_corruption_{}'.format(i), # 'name',
                'ray',                            # 'host',
                './corrupt_clang.py',             # 'compiler',
                '-O2',                            # 'optl',
                '--corrupt={}'.format(choice),    # 'switches',
                'd',                              # 'precision',
                '0x3ffbccccccccccccd000',         # 'score_hex',
                '0.1000000000000000055511151231257827021181583404541015625',
                                                  # 'score',
                'NULL',                           # 'resultfile',
                '0x3ffbccccccccccccd000',         # 'comparison_hex',
                '0.1000000000000000055511151231257827021181583404541015625',
                                                  # 'comparison',
                'executable_name',                # 'file',
                '0',                              # 'nanosec',
                ])

        subp.check_call(['flit', 'import',
                         '--dbfile', args.output,
                         fout.name])

if __name__ == '__main__':
    main(sys.argv[1:])
