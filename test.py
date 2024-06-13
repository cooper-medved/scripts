import sys
import time
import os
import json
import timeit

def calculate_latency(appName):
    timestamp = int((time.time() * 1000) - 59000)
    print(f"{timestamp} #############################")
    input_filename_sink = "/home/cc/storm/riot-bench/output/sink-ETLTopologySYS-SENML-6.6667.log"
    input_filename_spout = "/home/cc/storm/riot-bench/output/spout-ETLTopologySYS-SENML-6.6667.log1175000000001"
    output_filename = "/home/cc/storm/riot-bench/output/one-minute.log"

    data_to_cut = []
    one_minute_data = []

    # Read sink data and store entries from the last minute
    try:
        with open(input_filename_sink, "r") as f_sink, open(output_filename, "w") as dest_file:
            print("Opened sink file")
            for line_sink in f_sink:
                if not line_sink.strip():
                    continue
                ts_sink, process_id_sink = line_sink.strip().split(',')
                ts_sink = int(ts_sink)
                if ts_sink >= timestamp:
                    dest_file.write(f"{ts_sink},{process_id_sink}\n")
                    one_minute_data.append((ts_sink, int(process_id_sink)))
                    data_to_cut.append(line_sink)
                else:
                    break
        print("One-minute data stored in", output_filename)
    except Exception as e:
        print(f"Error processing sink data: {e}")
        return 0, 0, None

    # Remove the processed data from the sink file
    try:
        with open(input_filename_sink, "r") as f, open(input_filename_sink + ".temp", "w") as fw:
            for line in f:
                if line not in data_to_cut:
                    fw.write(line)
        os.remove(input_filename_sink)
        os.rename(input_filename_sink + ".temp", input_filename_sink)
        print("Data cut from the sink file.")
    except Exception as e:
        print(f"Error updating sink file: {e}")
        return 0, 0, None

    # Calculate latency by matching process IDs in sink and spout data
    latency = []
    msid_set = set()
    try:
        with open(input_filename_spout, "r") as f_spout:
            spout_data = {int(line.split(',')[2]): int(line.split(',')[0]) for line in f_spout if len(line.split(',')) >= 3}
            for ts_sink, process_id_sink in one_minute_data:
                if process_id_sink in spout_data:
                    ts_spout = spout_data[process_id_sink]
                    latency1 = ts_sink - ts_spout
                    print(f"Latency for process_id {process_id_sink} is {latency1}")
                    latency.append(latency1)
                    msid_set.add(process_id_sink)
        throughput = len(one_minute_data) / 60  # Assuming 1 tuple per line and 60 seconds in a minute
        print(f"Throughput: {throughput} tuples/second")
    except Exception as e:
        print(f"Error processing spout data: {e}")
        return 0, 0, None

    # Calculate tail latency
    if latency:
        latency.sort()
        tail_latency = latency[int(len(latency) * 0.95)]
    else:
        tail_latency = 0

    print(f"Latency calculation completed. Throughput: {throughput}, Tail Latency (95th percentile): {tail_latency}")
    return tail_latency, throughput, msid_set

while True:
    result = {}
    start = timeit.default_timer() 
    result['latency'], result['throughput'] = calculate_latency("ETLTopologySYS")
    with open('/home/cc/storm/riot-bench/output/skopt_input_ETLTopologySys.txt', 'a+') as f: 
        f.write(json.dumps(result) + "\n")
    stop = timeit.default_timer()
    time_taken = stop - start
    print("Time taken:", time_taken)
    minute = 60 - (time_taken / 1000000)
    time.sleep(minute)
