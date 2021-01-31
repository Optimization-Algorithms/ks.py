#! /usr/bin/python


import yaml
import os
import argparse
import zipfile
import subprocess


def get_output_file(file_list):
    output = []
    for file_name in file_list:
        with open(file_name) as file:
            data = yaml.safe_load(file)
            output.append(data["DEBUG"])
            output.append(data["SOLUTION_FILE"])
    return output


def create_configs(name, base_conf):
    output_dir = os.path.join("test-config", name)
    subprocess.run(["ks-config-generator", name, base_conf, "-o", output_dir])

    config_file_list = [
        os.path.join(output_dir, file) for file in os.listdir(output_dir)
    ]
    return (output_dir, config_file_list)


def ks_runner(name, conf_dir):
    instance = os.path.join("instances", f"{name}.mps")
    time_file = f"{name}-time.csv"
    subprocess.run(
        ["python", "ks-runner.py", "-i", instance, "-c", conf_dir, "-o", time_file]
    )
    return time_file


def store_test_results(name, result_files, time_file):
    archive_name = f"{name}-results.zip"
    with zipfile.ZipFile(
        archive_name, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9
    ) as file:
        for res_file in result_files:
            if os.path.exists(res_file):
                file.write(res_file)
                os.remove(res_file)

        if os.path.exists(time_file):
            file.write(time_file)
            os.remove(time_file)


def store_test_config(name, config_files):
    archive_name = f"{name}-config.zip"
    with zipfile.ZipFile(
        archive_name, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9
    ) as file:
        for conf in config_files:
            root_dir = os.path.dirname(conf)
            prev_dir = os.getcwd()
            os.chdir(root_dir)
            base_name = os.path.basename(conf)
            file.write(base_name)
            os.remove(base_name)
            os.chdir(prev_dir)



def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("name")
    parser.add_argument("config")

    return parser.parse_args()


def main():
    args = parse_args()
    output_dir, config_file_list = create_configs(args.name, args.config)
    result_files = get_output_file(config_file_list)
    time_file = ks_runner(args.name, output_dir)

    store_test_results(args.name, result_files, time_file)
    store_test_config(args.name, config_file_list)

    os.rmdir(output_dir)


if __name__ == "__main__":
    main()
