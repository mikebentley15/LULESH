#!/usr/bin/env python
'''
Parses the results of the LULESH injection experiment and generates statistics.
'''

import ast
import argparse
import collections
import csv
import os
import sys

SymbolTuple = collections.namedtuple(
    'SymbolTuple', 'src symbol demangled fname lineno')

class TestRun:
    '''
    Represents a bisect test run with corruption.
    
    Has the following attributes:
    - rows: (list(dict)) the rows given in the constructor
    - testid: (int) the id from the corruptions.sqlite database row
    - bisectnum: (int) which bisect run it was
    - compiler: (string) compiler used.  probably corrupt_clang.py
    - optl: (string) optimization level (e.g. '-O2')
    - switches: (string) says what to corrupt
    - precision: (string) precision used. (e.g. 'double')
    - testcase: (string) test case name. (e.g. 'LuleshTest')
    - completed_row: (dict) the final row specifying how it completed
    - succeeded_lib: (bool) succeeded in the library bisect phase (intel only)
    - succeeded_src: (bool) succeeded in the source bisect phase
    - succeeded_sym: (bool) succeeded in the symbol bisect phase
    - succeeded_all: (bool) succeeded in all phases (same as succeeded_sym)
    - return_code: (int) 0 if succeeded_all else 1
    - bisectdir: (string) directory where bisect files are located
        (e.g. 'bisect-15')
    - corrupt_file: (string) file that was to be corrupted
    - corrupt_symbol: (string) demangled symbol that was to be corrupted
    - corrupt_instruction: (int) which instruction number to corrupt
    - corrupt_val: (float) value to inject
    - corrupt_op: (string) operation to inject,
        one of ('ADD', 'SUB', 'DIV', 'MUL')
    - found_libs: (list(string)) found libraries using bisect
    - found_files: (list(string)) found files using bisect
    - found_symbols: (list(SymbolTuple)) found symbols using bisect
    - file_score_map: ({string: float}) found file to score mapping
    - symbol_score_map: ({SymbolTuple: float}) found symbol to score mapping
    '''

    def __init__(self, rows):
        'Parses the rows and populates the TestRun object'
        assert len(rows) > 0
        assert len([x for x in rows if x['type'] == 'completed']) == 1
        for col in ('testid', 'bisectnum', 'compiler', 'optl', 'switches',
                    'precision', 'testcase'):
            assert all(row[col] == rows[0][col] for row in rows), col
        self.rows = rows
        self.testid = int(rows[0]['testid'])
        self.bisectnum = int(rows[0]['bisectnum'])
        self.compiler = rows[0]['compiler']
        self.optl = rows[0]['optl']
        self.switches = rows[0]['switches']
        self.precision = rows[0]['precision']
        self.testcase = rows[0]['testcase']

        # See the success
        self.completed_row = [x for x in self.rows if x['type'] == 'completed'][0]
        self.succeeded_lib = 'lib' in self.completed_row['name']
        self.succeeded_src = 'src' in self.completed_row['name']
        self.succeeded_sym = 'sym' in self.completed_row['name']
        self.succeeded_all = self.completed_row['return'] == '0'
        self.return_code = int(self.completed_row['return'])

        self.bisectdir = 'bisect-{:02d}'.format(self.bisectnum)

        # parse switches into separate categories
        switch_split = self.switches.split()[1].split(',')
        assert len(switch_split) == 5
        self.corrupt_file = switch_split[0]
        self.corrupt_symbol = switch_split[1]
        self.corrupt_instruction = int(switch_split[2])
        self.corrupt_val = float(switch_split[3])
        self.corrupt_op = switch_split[4]

        # capture libraries, files, and symbols with comparison values
        file_score_tuples = [eval(x['name']) for x in self.rows
                             if x['type'] == 'src']
        symbol_score_tuples = [eval(x['name']) for x in self.rows
                               if x['type'] == 'sym']
        self.file_score_map = dict(file_score_tuples)
        self.symbol_score_map = dict(symbol_score_tuples)
        self.found_libs = sorted([x['name'] for x in self.rows
                                  if x['type'] == 'lib'])
        self.found_files = sorted(self.file_score_map.keys())
        self.found_symbols = sorted(self.symbol_score_map.keys())

def parse_args(arguments):
    'Parses the command-line arguments'
    parser = argparse.ArgumentParser(
        description='''
            Parses the results of the LULESH injection experiment and generates
            statistics.  You give the experimental results directory that
            contains auto-bisect.csv and each of the bisect directories.  Each
            bisect directory is expected to have bisect.log.''')
    parser.add_argument('-C', '--directory', default='.',
                        help='''
                            Directory containing LULESH results.  Defaults to
                            the current directory.
                            ''')
    return parser.parse_args(arguments)

def main(arguments):
    'Main logic here'
    args = parse_args(arguments)
    os.chdir(args.directory)
    with open('auto-bisect.csv', 'r') as fin:
        reader = csv.DictReader(fin)
        rows = [row for row in reader]
    rows_by_testid = collections.defaultdict(list)
    for row in rows:
        rows_by_testid[row['testid']].append(row)
    test_runs = sorted([TestRun(v) for k, v in rows_by_testid.items()],
                       key=lambda x: x.testid)

    exact_finds = 0                # 1. found exact same function
    indirect_finds = 0             # 2. found function that calls injected one
    failure_finds = 0              # 3. found the wrong thing
    failure_nofinds = 0            # 4. did not find function
    not_measurable = 0             # 5. injection not measurable

    file_histogram = collections.Counter()            # file finds -> count
    symbol_histogram = collections.Counter()          # symbol finds -> count
    indirect_finds_histogram = collections.Counter()  # symbol finds -> count

    test_run_count = len(test_runs)
    

    for test_run in test_runs:
        file_histogram[len(test_run.found_files)] += 1
        symbol_histogram[len(test_run.found_symbols)] += 1
        if (len(test_run.found_files) == 1
            and len(test_run.found_symbols) == 1
            and test_run.corrupt_file == test_run.found_files[0]
            and test_run.corrupt_symbol == test_run.found_symbols[0].symbol):
            exact_finds += 1
        elif len(test_run.found_files) > 0 and len(test_run.found_symbols) > 0:
            found_symbol_names = [x.symbol for x in test_run.found_symbols]
            assert test_run.corrupt_symbol not in found_symbol_names
            indirect_finds += 1
            indirect_finds_histogram[len(found_symbol_names)] += 1
        # I don't have a way of measuring failure_finds since the bisect run
        # would fail early if this ever happened.  That is because the bisect
        # algorithm has a built-in assertion at the end checking that the
        # compliment of found things produces a good score.
        elif not test_run.succeeded_all:
            failure_nofinds += 1
        else:
            assert test_run.succeeded_all
            assert len(test_run.found_libs) == 0
            assert len(test_run.found_files) == 0
            assert len(test_run.found_symbols) == 0
            not_measurable += 1

    # Print out the statistical report
    # TODO: calculate percentages with confidence intervals (i.e. error bars)
    print('Statistical Report:')
    print('  Total #:                       ', test_run_count)
    print('    1. success: exact finds:     ', exact_finds)
    print('    2. success: indirect finds:  ', indirect_finds)
    print('    3. failure: bad finds:       ', failure_finds)
    print('    4. failure: no finds:        ', failure_nofinds)
    print('    5. n/a:     not measurable:  ', not_measurable)
    print('  File histogram:')
    for key, value in sorted(file_histogram.items()):
        print('    {} found: {}'.format(key, value))
    print('  Symbol histogram:')
    for key, value in sorted(symbol_histogram.items()):
        print('    {} found: {}'.format(key, value))
    print('  Symbol histogram when not an exact find:')
    for key, value in sorted(indirect_finds_histogram.items()):
        print('    {} found: {}'.format(key, value))

if __name__ == '__main__':
    main(sys.argv[1:])
