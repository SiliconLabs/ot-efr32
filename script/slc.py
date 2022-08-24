#!/usr/bin/env python3

from genericpath import isdir
import logging
import pathlib
import platform
import subprocess
import time
from zipfile import ZipFile
import requests
import yaml
import shutil
import os
from efr32 import Board
from script.util import execute_and_log

# ==============================================================================
# System paths
# ==============================================================================
script_dir = os.path.dirname(os.path.realpath(__file__))
repo_dir = os.path.realpath(f"{script_dir}/../")
sdk_dir = os.path.realpath(f"{repo_dir}/third_party/silabs/gecko_sdk")

# ==============================================================================
# Class definitions
# ==============================================================================
class SlcProjectTemplate:
    def __init__(self, slcp_path: str) -> None:
        self.slcp_path = slcp_path

        with open(slcp_path) as file:
            self.slcp = yaml.load(file, Loader=yaml.FullLoader)
            self.name = self.slcp['project_name']

    def __str__(self) -> str:
        return self.name

    def __hash__(self) -> str:
        return self.slcp_path

class GeneratedProject:
    def __init__(self,
                    project: SlcProjectTemplate,
                    board: Board,
                    export_destination: str,
                    export_templates: str = "",
                    sdk: str = sdk_dir,
                    name: str = "",
                    config_string: str = "",
                    copy: bool = False,
                    clean: bool = True,
                    clear_cache: bool = False,
                    dry_run: bool = False,
                    with_components: str = None,
                    without_components: str = None,
                    output_type: str = "makefile",
                    slc_executable: str = "slc",
                    rename_templates: dict[str,str] = dict(),
                    rename_output_files: dict[str,str] = dict(),
                    remove_output_files: list[str] = list()):
        self.project = project
        self.board = board
        self.export_destination = export_destination
        self.export_templates = export_templates
        self.clear_cache = clear_cache
        self.command = []
        self.copy = copy
        self.sdk = sdk
        self.time = time
        self.verbose = True
        self.verbosity_level = 1
        self.clean = clean
        self.dry_run = dry_run
        self.output_type = output_type
        self.slc_executable = slc_executable

        self.name = self.project.slcp_path

        # Build "with" components list
        self.with_components = [str(self.board)]
        if with_components:
            self.with_components.extend(with_components.split(sep=","))

        # Build "without" components list
        self.without_components = []
        if without_components:
            self.without_components.extend(without_components.split(sep=","))

        # Parse "configuration" options.
        # - Formatted "<config_1>:<val_1>,<config_2>:<val_2>,..."
        # Ex: config = "SL_HEAP_SIZE:16384,SL_STACK_SIZE:4608"
        self.config = {}
        if config_string:
            config_list = config_string.split(",")
            for single_config_string in config_list:
                # Ex: c = "<config>:<val>"
                c = single_config_string.split(":")
                self.config[c[0]] = c[1]

        # log file path
        timestamp = time.strftime("%Y-%m-%dT%H%M%S")
        self.log_file = f'{self.export_destination}/{self.project.name}_{str(self.board)}_generate_{timestamp}.log'

        self.rename_templates    = rename_templates
        self.rename_output_files = rename_output_files
        self.remove_output_files = remove_output_files

    def __str__(self) -> str:
        return self.name

    def build_command(self):
        self.command = [f"{self.slc_executable}"]

        if self.verbose:
            self.command.append(f"--verbose={self.verbosity_level}")

        self.command.append("generate")

        if self.sdk:
            self.command.append(f"--sdk={self.sdk}")

        # Specify .slcp path
        self.command.extend(["--project-file", self.project.slcp_path])

        # Output type
        if self.with_components:
            self.command.extend(["--output-type", self.output_type])

        if self.copy:
            # Copy all source files
            self.command.append("-cp")
        else:
            self.command.append("--no-copy")

        if self.clear_cache:
            # Clear component cache
            self.command.append("--clear-cache")

        # Specify which export_templates to use
        if self.export_templates:
            self.command.append(f"--export-templates={self.export_templates}")

        # Specify output dir for generated project
        self.command.extend([f"--export-destination={self.export_destination}"])

        # Specify "with" components
        if self.with_components:
            self.command.extend(["--with"])
            comma_separated_components = ",".join(self.with_components)
            if comma_separated_components[:-1] == ",": del comma_separated_components[:-1]
            self.command.append(",".join(self.with_components))

        # Specify "without" components
        if self.without_components:
            self.command.extend(["--without"])
            self.command.append(",".join(self.without_components))

        # Add any configuration
        if self.config:
            self.command.extend(["--configuration"])
            self.command.extend(",".join(self.config))

    def get_command_string(self):
        '''Returns the command and its args as a string'''
        return ' '.join(self.command)

    def generate(self):
        # Set up export_destination
        if self.clean and not self.dry_run:
            try:
                shutil.rmtree(self.export_destination)
            except FileNotFoundError as e:
                # Ignore this error
                pass

        # Create export destination
        pathlib.Path(self.export_destination).mkdir(parents=True, exist_ok=True)

        if not self.command:
            self.build_command()

        # Create temporary template copies
        for src,dst in self.rename_templates.items():
            src_absolute = pathlib.Path(f"{self.export_templates}/{src}")
            dst_absolute = pathlib.Path(f"{self.export_templates}/{dst}")
            shutil.copyfile(
                src = src_absolute,
                dst = dst_absolute,
            )
            print(f"Copied '{src_absolute}' to '{dst_absolute}'")

        execute_and_log(self.command, self.log_file)
        print(f"Project generation logged to: {self.log_file}")

        # Delete temporary template copies
        for src,dst in self.rename_templates.items():
            dst_absolute = pathlib.Path(f"{self.export_templates}/{dst}")
            os.remove(dst_absolute)
            print(f"Deleted temporary file '{dst_absolute}'")

        # Perform any output file renaming
        for src,dst in self.rename_output_files.items():
            src_absolute = pathlib.Path(f"{self.export_destination}/{src}")
            dst_absolute = pathlib.Path(f"{self.export_destination}/{dst}")
            os.rename(
                src = src_absolute,
                dst = dst_absolute,
            )
            print(f"Renamed '{src_absolute}' to '{dst_absolute}'")

        # Remove specified output files
        for f in self.remove_output_files:
            f_absolute = pathlib.Path(f"{self.export_destination}/{f}")
            if os.path.isfile(f_absolute):
                os.remove(f_absolute)
            elif os.path.isdir(f_absolute):
                shutil.rmtree(f_absolute, ignore_errors=True)

class SlcInstallation:
    slc_install_dir_default = f"{repo_dir}/third_party/silabs/slc"
    slc_install_dir = os.environ.get("SLC_INSTALL_DIR") or slc_install_dir_default

    def __init__(self, force_install: bool) -> None:
        self.executable = ""
        if force_install:
            self.install()
        else:
            self.find()
            if not self.executable or force_install:
                logging.warning("No slc-cli installation was found.")
                self.install()
            pass

    def find(self) -> bool:
        if self.executable:
            return True

        commands_to_try = ["slc", "slc-cli"]
        for cmd in commands_to_try:
            try:
                subprocess.call(cmd)

                # Command executed successfully, save it
                self.executable = cmd
                return True
            except FileNotFoundError:
                # Command doesn't exist
                # Check if slc-cli was downloaded previously
                downloaded_slc = f"{self.slc_install_dir}/slc_cli/bin/slc-cli/slc-cli"
                if os.path.exists(downloaded_slc):
                    self.executable = downloaded_slc
                continue
        pass

        # Command not found
        return False

    def install(self):
        logging.info("Installing slc-cli...")

        # Get OS type
        my_os = platform.system().lower()
        os_type_overrides = {
            "darwin": "mac",
        }
        os_type = os_type_overrides[my_os] if my_os in os_type_overrides else my_os

        # Download
        zip_url = f"https://www.silabs.com/documents/login/software/slc_cli_{os_type}.zip"
        downloaded_zip_path = f"{repo_dir}/third_party/silabs/slc/slc_cli_{os_type}.zip"

        logging.debug(f'Downloading \'{downloaded_zip_path}\' from \'{zip_url}\'')
        r = requests.get(zip_url, stream=True)
        with open(downloaded_zip_path, "wb") as zip_file:
            for chunk in r.iter_content(chunk_size=1024):
                # writing one chunk at a time zip_file
                if chunk:
                    zip_file.write(chunk)

        # Extract all the contents of zip file to SLC_INSTALL_DIR

        logging.debug(f'Extracting \'{downloaded_zip_path}\' to \'{self.slc_install_dir}\'')
        with ZipFile(downloaded_zip_path, 'r') as zip_file:
            zip_file.extractall(path=self.slc_install_dir)
        logging.debug(f'Extract successful')