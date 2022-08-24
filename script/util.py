#!/usr/bin/env python3

import logging
import subprocess

def execute_and_log(command: list[str], log_file: str, dry_run: bool = False):
    with open(log_file, 'ab') as log:
        command_str = ' '.join(command)
        output_command_str = f">>>> {command_str}\n\n"
        log.write(bytes(output_command_str, encoding="utf-8"))
        logging.debug(output_command_str)

        if dry_run:
            return

        process = subprocess.Popen(
            command, shell=False, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        while True:
            output = process.stdout.readline()
            if process.poll() is not None:
                break
            if output:
                print(output.decode("utf-8"), end='')
                log.write(output)
        rc = process.poll()

        if rc:
            exit(rc)