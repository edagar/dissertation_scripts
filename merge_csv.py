#! /usr/bin/python2

import sys

def key_func(item):
    return item[0]

def update_tup(tup, n):
    tup[1] += n
    print("update_tup: %s, %d\n" % (str(tup), n))

def present(val, data):
    for d in data:
        if d[0] == val:
            return d
    return None

def merge(names):
    lines = []

    for name in names:
        with open(name, "r") as f:
            lines.append(f.readlines())        

    out = lines[0]
    data = [[int(l.split(",")[0]), int(l.split(",")[1].strip())] for l in out]    
    data.sort(key = key_func)

    for entries in lines[1:]:
        for line in entries:
            tup = present(int(line.split(",")[0]), data)
            if tup:
                update_tup(tup, int(line.split(",")[1].strip()))
            else:
                data.append([int(line.split(",")[0]), int(line.split(",")[1].strip())])

        data.sort(key = key_func)

    with open("out.csv", "w") as f:
        for tup in data:
            #if tup[1] > 1:
            f.write("%d,%d\n" % (tup[0], tup[1]))

if __name__ == "__main__":
    names = [n for n in sys.argv[1:]]
    merge(names)
