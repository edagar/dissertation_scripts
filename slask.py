import argparse
from sys import exit

parser = argparse.argumentparser()

parser.add_argument('--reset', action='store_const', const=true, default=none)

parser.add_argument('--cores', '-c')
parser.add_argument('--mem', '-m')

parser.add_argument('--phoronix', action='store_const', const=true, default=none)

parser.add_argument('--entry', '-i')
parser.add_argument('--exit', '-o')

args = parser.parse_args()
print(args, "\n\n")


if not (args.reset or (args.entry and args.exit) or args.phoronix):
    print("usage..")
    exit(1)

print("a okay!\n\n")

if args.reset:
    print("reseting..\n")

if args.phoronix:
    print("spawning phoronix benchmark\n")

if args.entry and args.exit:
    print("setting up benchmark environment (entry: %s, exit: %s)\n" % 
            (args.entry, args.exit)
         )
