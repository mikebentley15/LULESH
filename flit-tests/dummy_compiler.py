#!/usr/bin/env python3
'''
Dummy compiler that simply symbolically links to already created object files.
'''

import argparse
import os
import sys

def parse_args(arguments):
    '''
    Parses arguments relevant to this script and returns the parsed arguments
    as well as the remaining arguments to be passed along.

    @return (parsed_args, remaining_args)
      parsed_args: is a Namespace object with the attributes described above
      remaining_args: unparsed arguments that can be passed on to the compiler
    '''
    parser = argparse.ArgumentParser(
        description='''
            Dummy compiler that simply symbolically links to already created
            object files.
            ''')
    parser.add_argument('-o', dest='outfile', metavar='outfile', type=str,
        required=True)
    parser.add_argument('-c', action='store_true', required=True)
    parser.add_argument('--object-dir', dest='objdir', type=str, required=True)
    parser.add_argument('remainder', nargs=argparse.REMAINDER)
    args = parser.parse_args(arguments)
    return (args, args.remainder)

def main(arguments):
    'Main logic here'
    args, remaining = parse_args(arguments)
    print('parsed = {}'.format(args))
    print('remaining = {}'.format(remaining))

    print('Creating symbolic link instead of recompiling')
    fromobj = os.path.join(args.objdir, os.path.basename(args.outfile))
    toobj = args.outfile
    print('  {} -> {}'.format(fromobj, toobj))
    #os.symlink(fromobj, toobj)

if __name__ == '__main__':
    main(sys.argv[1:])
