from  statistics import median, stdev

def _val(val, n):
    if n > 1:
        return [val for _ in range(n)]
    return val
        
def stats_lantecy_cdf(filename):
    with open(filename, "r") as f:
        lines = f.readlines()

    values = []

    for line in lines:
        tup = (int(line.strip().split(",")[0]), int(line.strip().split(",")[1]))
        [values.append(tup[0]/1000) for _ in range(tup[1])]

    return min(values), max(values), median(values), stdev(values) 


# test case 1 cdf
#print(stats_lantecy_cdf("low_lat_kernel/testpmd_latency_merged.csv"))

#["low_lat_kernel/noisy_neighbour/latency_4_pinned_merged.csv", "low_lat_kernel/noisy_neighbour/latency_4_merged.csv"

#print(stats_lantecy_cdf("low_lat_kernel/noisy_neighbour/latency_4_merged.csv"))


#print(stats_lantecy_cdf("latency/testpmd/20170501/latency_10x10_5.csv"))

#print(stats_lantecy_cdf("latency/host/20170501/latency_10x5_1.csv"))
#print(stats_lantecy_cdf("latency/container/20170501/latency_10x5_merged.csv"))







#print(stats_lantecy_cdf("latency/l2fwd/merged.csv"))
#print(stats_lantecy_cdf("latency/container/20170501/latency_10x5_merged.csv"))
print(stats_lantecy_cdf("latency/host/20170501/latency_10x5_1.csv"))
