import subprocess
import argparse
import time
import json
import urllib2
from urllib import url_encode


# 900 seconds = 15 minutes
SOCKET_TIMEOUT = 900


def set_socket_timeout():
    import socket
    socket.setdefaulttimeout(SOCKET_TIMEOUT)


def generate_rules(app, support, confidence, backend_url, retry_times = 3):
    url_params = url_encode({
        'applicationName': app,
        'minSupport': support,
        'minConfidence': confidence
    })
    url = "{}?{}".format(backend_url, url_params)
    request = urllib2.Request(url)

    data = None
    execution_time = None

    for i in xrange(retry_times):
        try:
            start = time.time()
            response = urllib2.urlopen(request)
            data = response.read()
            execution_time = time.time() - start
            break
        except urllib2.URLError as e:
            continue

    return data, execution_time


def main(args):
    set_socket_timeout()
    subprocess.check_call(["mkdir", "-p", args.out_dir])
    app = args.app_name
    delta_confidence = (args.max_confidence - args.min_confidence) / (args.confidence_sample_size - 1)
    delta_support = (args.max_support - args.min_support) / (args.support_sample_size - 1)
    sample_index = 0

    for confidence_index in xrange(args.confidence_sample_size):
        for support_index in xrange(args.support_sample_size):
            sample_index += 1
            confidence = args.min_confidence + delta_confidence * confidence_index
            support = args.min_support + delta_support * support_index

            #print "support: {}  confidence: {}".format(support, confidence)

            data, execution_time = generate_rules(app, support, confidence)
            sample_dir = os.path.join(args.out_dir, "sample_{}".format(sample_index))
            subporcess.check_call(["mkdir", sample_dir])

            with open(os.path.join(sample_dir, "meta.json"), 'w') as meta_data:
                json.dump({
                    'support': support,
                    'confidence': confidence,
                    'execution_time': execution_time
                }, meta_data)

            if data != None:
                with open(os.path.join(sample_dir, "data.json"), 'w') as rule_data:
                    rule_data.write(data)


if __name__ == '__main__':
    parser = argparse.ArgumentParser("")
    parser.add_argument("--min-confidence", type = float, default = 0.3, help = "Confidence range low point")
    parser.add_argument("--max-confidence", type = float, default = 0.95, help = "Confidence range high point")
    parser.add_argument("--confidence-sample-size", type = int, default = 10, help = "How many samples to take from confidence range")
    parser.add_argument("--min-support", type = float, default = 0.001, help = "Support range low point")
    parser.add_argument("--max-support", type = float, default = 0.01, help = "Support range high point")
    parser.add_argument("--support-sample-size", type = int, default = 10, help = "How many samples to take from support range")
    parser.add_argument("--back-end-url", default = "localhost:44444")
    parser.add_argument("app_name", help = "Mobile application name for which to perform the measurements")
    parser.add_argument("out_dir", help = "Path to output directory. Created, if does not exist.")
    args = parser.parse_args()
    main(args)
