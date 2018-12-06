import argparse
import os
import signal
import subprocess
import sys
import time

proc = None


def run(command):
    global proc
    try:
        proc = subprocess.Popen(command, stdout=sys.stdout.buffer,
                                stderr=sys.stderr.buffer)
        exit_code = proc.wait()
        if exit_code != 0:
            raise subprocess.CalledProcessError(exit_code, command[0])
    except subprocess.CalledProcessError as e:
        print(str(e))


def sigint_handler(signal_no, frame):
    if proc is not None:
        os.kill(proc.pid, signal.SIGINT)
    time.sleep(0.25)
    sys.exit(0)


def main():
    signal.signal(signal.SIGINT, sigint_handler)

    parser = argparse.ArgumentParser()
    parser.add_argument('-t', '--type', required=True, type=str,
                        help='What Java class to run.',
                        choices=[
                            "solvers.Solve",
                            "wikipedia_indexer_cmd.Application",
                            "wikipedia_utils.WikiToText"
                        ])
    parser.add_argument('--heap', required=False, type=str, default="1G",
                        help='The size of the Java heap space as in -Xmx.')
    FLAGS, _ = parser.parse_known_args()

    # Print summary and ask for confirmation.
    print("About to run this configuration:")
    print("\t Class: {}".format(FLAGS.type))
    print("\t Heap size: {}".format(FLAGS.heap))
    print("\nDo you want to run this configuration? [y/N] ", end='',
          flush=True)
    opt = str(input())
    if opt.rstrip().lower() == "y":
        run(["bash", "exec.sh", FLAGS.type, FLAGS.heap])


if __name__ == "__main__":
    main()
