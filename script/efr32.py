#!/usr/bin/env python3

import glob
import yaml
import re
import os

# ==============================================================================
# System paths
# ==============================================================================
script_dir = os.path.dirname(os.path.realpath(__file__))
repo_dir = os.path.realpath(f"{script_dir}/../")
sdk_dir = os.path.realpath(f"{repo_dir}/third_party/silabs/gecko_sdk")

# ==============================================================================
# Global variables
# ==============================================================================
# Regex for matching various parts of the efr32 device string
efr32_device_regex = r""
# Group 1 - efr32 (product, optional)
efr32_device_regex += r"(?P<product>efr32)*"
# Group 2 - mg, bg, xg (family)
efr32_device_regex += r"(?P<family>[a-z]{2})"
# Group 3 - m (optional, modules only)
efr32_device_regex += r"(?P<module>m*)"
# Group 4 - 1, 12, 13, 21, 24, 210, 240 etc (series and configuration)
efr32_device_regex += r"(?P<series_config>\d{1,2})\d{0,1}"
# Group 5 - a, b, c, p, v (revision)
efr32_device_regex += r"(?P<revision>[a-z]{1})"
# Group 6 - xxx, a32, 032
efr32_device_regex += r"([a-z]{0,1}\d{1,3})"
# Group 7 - fXXX (flash size)
efr32_device_regex += r"(?P<flash>f\d{1,})*"
# Rest of line
efr32_device_regex += r".*"

# ==============================================================================
# Class definitions
# ==============================================================================
class Board:
    def __init__(self, board_string: str):
        self.board = board_string.lower()
        self.board_slcc = ""
        self.platform = ""
        self.get_component_file()
        self.get_platform()

    def __str__(self) -> str:
        return f"{self.board}"

    def get_component_file(self):
        '''Gets the latest revision .slcc file for a efr32 board'''
        if self.board_slcc:
            return self.board_slcc

        # Get all .slcc files that might be associated with the board
        glob_pattern = f"{sdk_dir}/hardware/board/component/{self.board}*.slcc"
        matching_files = glob.glob(glob_pattern)
        assert matching_files, f"No component file could be found for \"{self.board}\""

        # Filter out unwanted components
        matching_files = list(
            filter(lambda filename: 'support' not in filename, matching_files))

        matching_files.sort(reverse=True)
        self.board_slcc = matching_files[0]

        return self.board_slcc

    def get_platform(self):
        '''Determine board's platform'''
        if self.platform:
            return self.platform

        with open(self.get_component_file(), "r") as file:
            component = yaml.load(file, Loader=yaml.FullLoader)

            # Find the "board:device:" tag in the component
            for section, val in component:
                if section == "tag":
                    for tag in val:
                        m = re.match(pattern=r"board:device:(.*)", string=tag)
                        if m:
                            self.device_string = m.group(1)
                            break
                    break

        self.device = re.match(pattern=efr32_device_regex,
                               string=self.device_string).groupdict()
        d = self.device
        self.platform = f"{d['product']}{d['family']}{d['series_config']}"

        return self.platform
