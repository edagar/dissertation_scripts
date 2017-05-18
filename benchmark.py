#! /usr/bin/python2

import argparse
import os
from multiprocessing import Process
from start_single_container import run_phoronix_benchmark, setup_env, clear_huge_pages, popen


DUMP_FILE    = "bound_interfaces_client"
DEFAULT_SIZE = 60

def setup(entry, exit):
    setup_env(entry, exit, DUMP_FILE, run_container=False)    

def reset():
    """
        * unbind interfaces from dpdk driver
        * rebind interfaces to kernel driver
        * rebind interfaces to previous ip addrs
        * remove huge page mappings
    """

    with open(DUMP_FILE, "r") as f:
        lines = [l.strip() for l in f.readlines()]
        for line in lines:
            iface = eval(line)

            print("unbinding from PMD: %s\n" % str(iface[0]))
            popen('./run.sh "--unbind %s"' % iface[1], "r")

            print("rebinding to kernel driver: %s\n" % iface[0])
            popen('./run.sh "--bind=%s %s"' % (iface[2], iface[1]), "r")

            print("rebinding interface %s to ip addr %s\n" % (iface[0], iface[4]))
            popen("ifconfig %s %s" % (iface[0], iface[4]), "r")

    print("clearing hugepages..\n")
    clear_huge_pages()
    print("all done. exiting\n")
    exit(0)

benchmarks = ["latency", "throughput", "packet_sizes"]

def run(benchmark, size):
    if benchmark in benchmarks:
        if not size:
            size = DEFAULT_SIZE
        print("running benchmark: %s (packet size: %d)\n" % (benchmark, int(size)))

        cmd = "./start_%s.sh %s" % (benchmark, str(size))
        os.system(cmd)

    else:
        raise RuntimeError("Unkown benchmark: %s" % benchmark)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()

    parser.add_argument('--reset', action='store_const', const=True, default=None)
    parser.add_argument('--phoronix', action='store_const', const=True, default=None)
    parser.add_argument('--setup', action='store_const', const=True, default=None)
    parser.add_argument('--entry', '-i')
    parser.add_argument('--exit', '-o')

    parser.add_argument('--run', '-r', help="run benchmark")
    parser.add_argument('--size', '-s', help="specify packet size")

    args = parser.parse_args()

    if not (args.reset or (args.setup) or args.phoronix or args.run):
        parser.print_usage()
        parser.exit()
    
    if args.setup:
        if not args.entry and not args.exit:
                print("Need to specify entry and exit interfaces (got none)\n\n")
                parser.print_help()
                parser.exit()

        elif (args.entry or args.exit):
            if not (args.entry and args.exit):
                print("Need to specify entry and exit interfaces (got only one)\n\n")
                parser.print_help()
                parser.exit()

    if args.phoronix:
        phoronix_process = Process(target=run_phoronix_benchmark)
        phoronix_process.start()   

    if args.reset:
        reset()

    if args.setup:
        setup(args.entry, args.exit)

    if args.run:
        try:
            run(args.run.strip(), args.size)
        except RuntimeError as e:
            print("something went wrong: %s\n\n" % e)
            exit(1)

