#!/usr/bin/env python3

import sys
import time
import os
import json
import timeit
from loguru import logger

# Configure loguru logger
logger.add("latency_throughput_log.log", rotation="1 MB", retention="10 days", level="INFO")

def read_sink_data(input_filename_sink, timestamp):
    data_to_cut = []
    one_min_data = []

    try:
        with open(input_filename_sink, "r") as f_sink:
            logger.info("Opened sink file")
            for line_sink in f_sink:
                ts_sink, process_id_sink = line_sink.strip().split(",")
                ts_sink = int(ts_sink)
                if ts_sink < timestamp + 60000:
                    one_min_data.append((ts_sink, process_id_sink))
                    data_to_cut.append(line_sink)
                else:
                    break

    except Exception as e:
        logger.error(f"Error reading sink data: {e}")
    return one_min_data, data_to_cut

def write_one_min_data(output_filename, one_min_data):
    try:
        with open(output_filename, "w") as dest_file:
            for ts_sink, process_id in one_min_data:
                dest_file.write(f"{ts_sink},{process_id}\n")
            logger.info(f"One-minute data stored in {output_filename}")
    except Exception as e:
        logger.error(f"Error writing one-minute data: {e}")

def cut_sink_data(input_file_sink, data_to_cut):
    try:
        with open(input_file_sink, "r") as f, open(input_file_sink + ".temp", "w") as fw:
            for line in f:
                if line not in data_to_cut:
                    fw.write(line)
        os.rename(input_file_sink + ".temp", input_file_sink)
        logger.info("Data cut from the sink file.")

    except Exception as e:
        logger.error(f"Error cutting sink data: {e}")

def calc_latency(input_file_spout, one_min_data):
    latency = []
    try:
        with open(input_file_spout, "r") as f_spout:
            logger.info("Opened spout file")
            spout_data = f_spout.readlines()
            for ts_sink, process_id_sink in one_min_data:
                process_id_sink = int(process_id_sink)
                for line_spout in spout_data:
                    ts_spout, _, process_id_spout = line_spout.strip().split(",")[0:3]
                    ts_spout = int(ts_spout)
                    if process_id_sink == int(process_id_spout):
                        latency1 = ts_sink - ts_spout
                        latency.append(latency1)
                        break

    except Exception as e:
        logger.error(f"Error calculating latency: {e}")
    return latency

def calc_metrics(latency):
    if latency:
        latency.sort()
        throughput = len(latency)
        tail_latency = latency[int(len(latency) * 0.95)]
    else:
        throughput = 0
        tail_latency = 0

    return tail_latency, throughput

def calc_latency_for_app(app_name, input_file_sink, input_file_spout, output_filename):
    timestamp = int(time.time() * 1000) - 59000
    logger.info(f"{app_name}: Timestamp: {timestamp}")

    one_min_data, data_to_cut = read_sink_data(input_file_sink, timestamp)
    write_one_min_data(output_filename, one_min_data)
    cut_sink_data(input_file_sink, data_to_cut)

    latency = calc_latency(input_file_spout, one_min_data)
    tail_latency, throughput = calc_metrics(latency)

    logger.info(f"Latency calculation completed. Throughput: {throughput}, Tail latency: {tail_latency}")
    return tail_latency, throughput

def main():
    input_filename_sink = "/home/cc/storm/riot-bench/output/sink-IoTTrainTopologySYS-PLUG-2100-100.0.log"
    input_filename_spout = "/home/cc/storm/riot-bench/output/spout-IoTTrainTopologySYS-PLUG-2100-100.0.log"
    output_filename = "/home/cc/riot-bench/output/one-minute.log"

    while True:
        result = {}
        start = timeit.default_timer()
        result["latency"], result["throughput"] = calc_latency_for_app(
            "ETLTopologySYS", input_filename_sink, input_filename_spout, output_filename
        )
        try:
            with open("/home/cc/storm/riot-bench.output/skopt_input_ETLTopologySys.txt", "a+") as f:
                f.write(json.dumps(result) + "\n")
        except Exception as e:
            logger.error(f"Error writing results: {e}")
        stop = timeit.default_timer()
        time_taken = stop - start
        logger.info(f"Time taken: {time_taken} seconds")
        minute = 60 - time_taken
        time.sleep(max(0, minute))

if __name__ == "__main__":
    main()
