import matplotlib
import matplotlib.pyplot as plt
from matplotlib import mlab
from collections import Counter
import numpy as np
from math import floor, ceil

def plot_bar_latency(filenames):
    x = []
    y = []
    std = []

    for name in filenames:
        with open(name, "r") as f:
            lines = f.readlines()

            x.append([int(l.split(",")[0]) for l in lines])
            y.append([float(l.split(",")[1]) for l in lines])
            std.append([float(l.split(",")[2].strip()) for l in lines])

    for i in range(len(y)):
        y[i] = [val/1000.0 for val in y[i]]

    for i in range(len(std)):
        std[i] = [val/1000.0 for val in std[i]]

    fig, ax = plt.subplots()
    index = np.arange(len(y[0]))
    width = 0.25
    opacity=1.0

    for xc in range(0, 310, 10):
        plt.axhline(xc, color='k', linestyle='--', alpha=0.2)

    bars1 = plt.bar(index, y[0], width, alpha=opacity, color='b', yerr=std[0], label='OVS-DPDK in container')
    bars2 = plt.bar(index+width, y[1], width, alpha=opacity, color='g', yerr=std[1], label='OVS-DPDK on host')
    bars2 = plt.bar(index+width * 2, y[2], width, alpha=opacity, color='r', yerr=std[2], label='L2fwd')

    plt.title("Latency - microseconds")
    plt.xlabel("Packet size (bytes)")
    plt.ylabel("Latency (us)")
    plt.xticks(index + width, x[0])
    plt.legend(loc=2)
    plt.tight_layout()

    #render the figure and save it to a file
    #plt.savefig('testcase_1_latency_packet_sizes.png')
    plt.show()

def plot_bar(filenames):
    x = []
    y = []
    std = []

    for name in filenames:
        with open(name, "r") as f:
            lines = f.readlines()

            x.append([int(l.split(",")[0]) for l in lines])
            y.append([float(l.split(",")[1]) for l in lines])
            std.append([float(l.split(",")[2].strip()) for l in lines])


    for q in x:
        q[0] += 4

    fig, ax = plt.subplots()
    index = np.arange(len(y[0]))
    width = 0.25
    opacity=1.0

    for xc in range(0, 16, 1):
        plt.axhline(xc, color='k', linestyle='--', alpha=0.2)


    bars1 = plt.bar(index, y[0], width, alpha=opacity, color='b', yerr=std[0], label='OVS-DPDK in container')
    bars2 = plt.bar(index+width, y[1], width, alpha=opacity, color='g', yerr=std[1], label='OVS-DPDK on host')
    bars2 = plt.bar(index+width * 2, y[2], width, alpha=opacity, color='r', yerr=std[2], label='L2fwd')

    plt.title("Throughput - Million packets per second")
    plt.xlabel("Packet size (bytes)")
    plt.ylabel("MPPS")
    plt.xticks(index + width, x[0])
    plt.legend()
    plt.tight_layout()

    #render the figure and save it to a file
    #plt.savefig('test_case_1_mpps.png')

    plt.show()

def plot_latency(filenames):
    labels = ["OVS-DPDK in container", "OVS-DPDK on host", "L2fwd"]
    colors = ["b", "yellow", "r"]
    styles = ["b-", "g:", "r:"]

    opacities = [0.9, 0.9, 0.9]

    opacity=0.9

    _data = []

    for index, name in enumerate(filenames):
        with open(name, "r") as f:
            lines = f.readlines()

        data = [(float(l.split(",")[0]), float(l.split(",")[1].strip())) for l in lines]

        Z = [(d[0] / 1000.0) for d in data]
        _data += Z
        X2 = np.sort(Z)
        N = len(Z)
        F2 = np.array(range(N))/float(N)*100

        plt.plot(X2, F2, styles[index], label=labels[index], linewidth=2, alpha=opacities[index], antialiased=False)

    plt.title("Latency - Cumulative dist function")
    plt.xlabel("Latency (us)")
    plt.ylabel("CDF (%)")

    for xc in range(0, 110, 5):
        plt.axhline(xc, color='k', linestyle='--', alpha=0.2)


    xc = min(_data)
    while xc <= max(_data)+0.4:
        plt.axvline(xc, color='k', linestyle='--', alpha=0.2)
        xc += 0.4

    plt.xticks(np.arange(min(_data), max(_data)+0.4, 0.4), fontsize=6)
    plt.legend(loc=2, prop={'size': 10})
    plt.tight_layout()

    #plt.savefig('low_lat_config_latency_cdf.png')
    plt.show()

def plot_bar_limited_cpu(filenames):
    x = []
    y = []
    std = []

    for name in filenames:
        with open(name, "r") as f:
            lines = f.readlines()

            x.append([int(l.split(",")[0]) for l in lines])
            y.append([float(l.split(",")[1]) for l in lines])
            std.append([float(l.split(",")[2].strip()) for l in lines])

    for q in x:
        q[0] += 4


    fig, ax = plt.subplots()
    index = np.arange(len(y[0]))
    width = 0.15
    opacity=1.0

    for xc in range(1, 16):
        plt.axhline(xc, color='k', linestyle='--', alpha=0.2)

    bars1 = plt.bar(index,           y[0], width, alpha=opacity, yerr=std[0], color='b', label='100%')
    bars2 = plt.bar(index+width,     y[1], width, alpha=opacity, yerr=std[1], color='g', label='75%')
    bars2 = plt.bar(index+width * 2, y[2], width, alpha=opacity, yerr=std[2], color='r', label='75%')
    bars3 = plt.bar(index+width * 3, y[3], width, alpha=opacity, yerr=std[3], color='m', label='50%')
    bars4 = plt.bar(index+width * 4, y[4], width, alpha=opacity, yerr=std[4], color='y', label='12.5%')

    plt.title("Throughput - Million packets per second")
    plt.xlabel("Packet size (bytes)")
    plt.ylabel("MPPS")
    plt.xticks(index + width, x[0])
    plt.legend()
    plt.tight_layout()

    #render the figure and save it to a file
    #plt.savefig('mpps.pdf')
    #plt.savefig('percents_0.pdf')

    #plt.savefig('testcase_2_tp_1.png')
    #plt.savefig('testcase_1_mpps.png')

    plt.show()

def plot_bar_limited_cpu2(filenames):
    x = []
    y = []
    std = []

    for name in filenames:
        with open(name, "r") as f:
            lines = f.readlines()

            x.append([int(l.split(",")[0]) for l in lines])
            y.append([float(l.split(",")[1]) for l in lines])
            std.append([float(l.split(",")[2].strip()) for l in lines])

    fig, ax = plt.subplots()
    width = 0.15
    opacity=1.0

    colors = ['b', 'g', 'r', 'm', 'y']
    percents = ["100%", "75%", "50%", "25%", "12.5%"]

    for xc in range(1, 16):
        plt.axhline(xc, color='k', linestyle='--', alpha=0.4)

    print(y)
    values = []
    j = 0
    for i in range(len(y)+1):
        l = [v[j] for v in y]
        values.append(l)
        j += 1

    print(values)
    print(len(values))
    index = np.arange(len(values[0]))

    bars1 = plt.bar(index,           values[0], width, alpha=opacity, yerr=std[0], color='b', label='64')
    bars2 = plt.bar(index+width,     values[1], width, alpha=opacity, yerr=std[1], color='g', label='128')
    bars3 = plt.bar(index+width * 2, values[2], width, alpha=opacity, yerr=std[2], color='r', label='256')
    bars4 = plt.bar(index+width * 3, values[3], width, alpha=opacity, yerr=std[3], color='m', label='512')
    bars5 = plt.bar(index+width * 4, values[4], width, alpha=opacity, yerr=std[4], color='y', label='1024')
    bars6 = plt.bar(index+width * 5, values[5], width, alpha=opacity, yerr=std[5], color='c', label='1500')


    plt.title("Throughput - Million packets per second")
    plt.xlabel("CPU limitation")
    plt.ylabel("MPPS")

    plt.xticks(index + width, percents)
    plt.legend(loc=1)
    plt.tight_layout()

    #render the figure and save it to a file
    #plt.savefig('testcase_2_tp_2.png')

    plt.show()

def plot_bar_latency_limited_cpu(filenames):
    x = []
    y = []
    std = []

    for name in filenames:
        with open(name, "r") as f:
            lines = f.readlines()

            x.append([int(l.split(",")[0]) for l in lines])
            y.append([float(l.split(",")[1]) for l in lines])
            std.append([float(l.split(",")[2].strip()) for l in lines])

    for i in range(len(y)):
        y[i] = [val/1000.0 for val in y[i]]

    for i in range(len(std)):
        std[i] = [val/1000.0 for val in std[i]]

    fig, ax = plt.subplots()
    index = np.arange(len(y[0]))
    width = 0.15
    opacity=1.0

    for xc in range(1, 255, 10):
        plt.axhline(xc, color='k', linestyle='--', alpha=0.2)

    bars1 = plt.bar(index, y[0], width, alpha=opacity, color='b', label='100%')
    bars2 = plt.bar(index+width, y[1], width, alpha=opacity, color='g', label='75%')
    bars2 = plt.bar(index+width * 2, y[2], width, alpha=opacity, color='r', label='50%')
    bars3 = plt.bar(index+width * 3, y[3], width, alpha=opacity, color='m', label='25%')
    bars4 = plt.bar(index+width * 4, y[4], width, alpha=opacity, color='y', label='12.5%')

    plt.title("Latency - microseconds")
    plt.xlabel("Packet size (bytes)")
    plt.ylabel("Latency (us)")
    plt.xticks(index + width, x[0])
    plt.legend()
    plt.tight_layout()

    #render the figure and save it to a file
    #plt.savefig('mpps.pdf')
    #plt.savefig('percents_0.pdf')

    #plt.savefig('testcase_2_tp_1.png')

    plt.show()

def plot_bar_latency_limited_cpu2(filenames):
    x = []
    y = []
    std = []

    for name in filenames:
        with open(name, "r") as f:
            lines = f.readlines()

            x.append([int(l.split(",")[0]) for l in lines])
            y.append([float(l.split(",")[1]) for l in lines])
            std.append([float(l.split(",")[2].strip()) for l in lines])

    for i in range(len(y)):
        y[i] = [val/1000.0 for val in y[i]]

    for i in range(len(std)):
        std[i] = [val/1000.0 for val in std[i]]


    fig, ax = plt.subplots()
    width = 0.15
    opacity=1.0

    colors = ['b', 'g', 'r', 'm', 'y']
    percents = ["100%", "75%", "50%", "25%", "12.5%"]

    for xc in range(0, 270, 20):
        plt.axhline(xc, color='k', linestyle='--', alpha=0.2)

    values = []
    j = 0
    for i in range(len(y)+1):
        l = [v[j] for v in y]
        values.append(l)
        j += 1

    index = np.arange(len(values[0]))

    bars1 = plt.bar(index,           values[0], width, alpha=opacity, color='b', label='64 bytes')
    bars2 = plt.bar(index+width,     values[1], width, alpha=opacity, color='g', label='128 bytes')
    bars3 = plt.bar(index+width * 2, values[2], width, alpha=opacity, color='r', label='256 bytes')
    bars4 = plt.bar(index+width * 3, values[3], width, alpha=opacity, color='m', label='512 bytes')
    bars5 = plt.bar(index+width * 4, values[4], width, alpha=opacity, color='y', label='1024 bytes')
    bars6 = plt.bar(index+width * 5, values[5], width, alpha=opacity, color='c', label='1500 bytes')

    plt.title("Latency - microseconds")
    plt.xlabel("CPU limitation")
    plt.ylabel("Latency (us)")

    plt.xticks(index + width, percents)
    plt.legend(loc=2, prop={'size': 7})
    plt.tight_layout()

    #render the figure and save it to a file
    plt.savefig('testcase_2_latency.png')

    #plt.show()

def plot_latency_noisy_neighbour(filenames):
    labels = ["Pinned", "Not pinned"]
    colors = ["b", "yellow", "r"]
    styles = ["b-", "g:", "r:"]

    opacities = [1.0, 1.0]


    _data = []

    for index, name in enumerate(filenames):
        with open(name, "r") as f:
            lines = f.readlines()

        data = [(float(l.split(",")[0]), float(l.split(",")[1].strip())) for l in lines]

        Z = [(d[0] / 1000.0) for d in data]
        _data += Z
        X2 = np.sort(Z)
        N = len(Z)
        F2 = np.array(range(N))/float(N)*100

        plt.plot(X2, F2, styles[index], label=labels[index], linewidth=2, alpha=opacities[index], antialiased=False)

    plt.title("Latency - Cumulative dist function")
    plt.xlabel("Latency (us)")
    plt.ylabel("CDF (%)")

    for xc in range(0, 110, 5):
        plt.axhline(xc, color='k', linestyle='--', alpha=0.2)

    for xc in range(int(min(_data)), int(max(_data)+2), 2):
        plt.axvline(xc, color='k', linestyle='--', alpha=0.2)

    plt.xticks(np.arange(floor(min(_data)), ceil(max(_data)+1), 2.0), fontsize=8)
    plt.legend(loc=4, prop={'size': 16})
    plt.tight_layout()

    plt.savefig('testcase_3_latency_cdf.png')
    #plt.show()

def plot_bar_noisy_neighbour(filenames):
    x = []
    y = []
    std = []

    for name in filenames:
        with open(name, "r") as f:
            lines = f.readlines()

            x.append([int(l.split(",")[0]) for l in lines])
            y.append([float(l.split(",")[1]) for l in lines])
            std.append([float(l.split(",")[2].strip()) for l in lines])


    fig, ax = plt.subplots()
    index = np.arange(len(y[0]))
    width = 0.25
    opacity=1.0

    for xc in range(0, 16, 1):
        plt.axhline(xc, color='k', linestyle='--', alpha=0.2)


    bars1 = plt.bar(index, y[0], width, alpha=opacity, color='b', yerr=std[0], label='Pinned')
    bars2 = plt.bar(index+width, y[1], width, alpha=opacity, color='g', yerr=std[1], label='Not pinned')

    plt.title("Throughput - Million packets per second")
    plt.xlabel("Packet size (bytes)")
    plt.ylabel("MPPS")
    x[0][0] += 4
    plt.xticks(index + (width/2), x[0])
    plt.legend(prop={'size': 14})
    plt.tight_layout()

    #render the figure and save it to a file
    #plt.savefig('testcase_3_mpps.png')

    plt.show()



# test case 1

# throughput
#plot_bar(["low_lat_kernel/container_100_throughput.1.csv", "low_lat_kernel/host_throughput.1.csv", "low_lat_kernel/l2fwd_throughput.csv"])

# latency - cdf
#plot_latency(["low_lat_kernel/container_latency_merged.2.csv", "low_lat_kernel/host_latency_merged.2.csv", "low_lat_kernel/testpmd_latency_merged.csv"])

# latency - bars
#plot_bar_latency(["low_lat_kernel/container_100_latency.csv", "low_lat_kernel/host_latency.csv", "low_lat_kernel/testpmd_latency.csv"])


# test case 2

"""plot_bar_limited_cpu([
    "low_lat_kernel/cpu_lim/100_latency.csv",
    "low_lat_kernel/cpu_lim/75_latency.csv",
    "low_lat_kernel/cpu_lim/50_latency.csv",
    "low_lat_kernel/cpu_lim/25_latency.csv",
    "low_lat_kernel/cpu_lim/12.5_latency.csv"])

plot_bar_limited_cpu([
    "low_lat_kernel/cpu_lim/100_throughput.csv",
    "low_lat_kernel/cpu_lim/75_throughput.csv",
    "low_lat_kernel/cpu_lim/50_throughput.csv",
    "low_lat_kernel/cpu_lim/25_throughput.csv",
    "low_lat_kernel/cpu_lim/12.5_throughput.csv"])


plot_bar_limited_cpu([
    "low_lat_kernel/cpu_lim/100_throughput.csv",
    "low_lat_kernel/cpu_lim/75_throughput.csv",
    "low_lat_kernel/cpu_lim/50_throughput.csv",
    "low_lat_kernel/cpu_lim/25_throughput.csv",
    "low_lat_kernel/cpu_lim/12.5_throughput.csv"])

plot_bar_latency_limited_cpu2([
    "low_lat_kernel/cpu_lim/100_latency.csv",
    "low_lat_kernel/cpu_lim/75_latency.csv",
    "low_lat_kernel/cpu_lim/50_latency.csv",
    "low_lat_kernel/cpu_lim/25_latency.csv",
    "low_lat_kernel/cpu_lim/12.5_latency.csv"])"""

# test case 3

# latency - cdf
#plot_latency_noisy_neighbour(["low_lat_kernel/noisy_neighbour/latency_4_pinned_merged.csv", "low_lat_kernel/noisy_neighbour/latency_4_merged.csv"])

"""plot_bar_noisy_neighbour([
                            "low_lat_kernel/noisy_neighbour/throughput_4_pinned.csv",
                            "low_lat_kernel/noisy_neighbour/throughput_4.csv"
                        ])"""
