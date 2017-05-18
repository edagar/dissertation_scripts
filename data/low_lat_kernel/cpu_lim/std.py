#! /usr/bin/python2

import sys

def show(fn):
    with open(fn, "r") as f:
        lines = f.readlines()

    for line in lines:
        parts = line.strip().split(",")
        tup = (int(parts[0]), float(parts[1])/1000.0, float(parts[2])/1000.0)
        print("size: %d, value: %f, stdev: %f\n" % (tup[0], tup[1], tup[2]))

if __name__ == "__main__":
    if len(sys.argv) > 1:
        show(sys.argv[1])
