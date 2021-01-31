#! /usr/bin/python

import argparse
import subprocess
import time
import os


class Timer:
    def __init__(self):
        self.start = time.time_ns()

    def stop(self):
        end = time.time_ns()
        duration = (end - self.start) / 1e9
        return duration


def run_instances(instance, configs):
    exec_time = {}
    for conf in configs:
        try:
            print("Running", instance, conf)
            timer = Timer()
            subprocess.run(["python", "ks.py", "-c", conf, instance])
        except:
            pass
        else:
            time = timer.stop()
            conf = os.path.basename(conf)
            exec_time[conf] = time

    return exec_time


def save_results(exec_time, output_file):
    with open(output_file, "w") as file:
        for conf, result in exec_time.items():
            print(f"{conf},{result}", file=file)


def parse_args():
    parser = argparse.ArgumentParser(
        description="Run ks.py with the given set of configurations"
    )
    parser.add_argument("-i", "--instance", required=True)
    parser.add_argument("-c", "--config", nargs="+")
    parser.add_argument("-o", "--output")

    return parser.parse_args()


def main():
    args = parse_args()

    if len(args.config) == 1:
        dir_name = args.config[0]
        configs = [os.path.join(dir_name, file) for file in os.listdir(dir_name)]
    else:
        configs = args.config

    exec_time = run_instances(args.instance, configs)
    if args.output:
        save_results(exec_time, args.output)
    else:
        print(exec_time)


if __name__ == "__main__":
    main()
