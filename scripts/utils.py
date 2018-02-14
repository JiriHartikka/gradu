import os
import re
import json


def read_data(data_dir):
    samples = []

    for dir_name in os.listdir(data_dir):
        if re.match("sample_\d+", dir_name):
            with open(os.path.join(data_dir, dir_name, "data.json"), 'r') as f:
                data = json.load(f)
            with open(os.path.join(data_dir, dir_name, "meta.json"), 'r') as f:
                meta_data = json.load(f)
            samples.append((meta_data, data))

    return samples