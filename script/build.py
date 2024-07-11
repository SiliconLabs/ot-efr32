#!/usr/bin/env python3
#
#  Copyright (c) 2024, The OpenThread Authors.
#  All rights reserved.
#
#  Redistribution and use in source and binary forms, with or without
#  modification, are permitted provided that the following conditions are met:
#  1. Redistributions of source code must retain the above copyright
#     notice, this list of conditions and the following disclaimer.
#  2. Redistributions in binary form must reproduce the above copyright
#     notice, this list of conditions and the following disclaimer in the
#     documentation and/or other materials provided with the distribution.
#  3. Neither the name of the copyright holder nor the
#     names of its contributors may be used to endorse or promote products
#     derived from this software without specific prior written permission.
#
#  THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
#  AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
#  IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
#  ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE
#  LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
#  CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
#  SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
#  INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
#  CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
#  ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
#  POSSIBILITY OF SUCH DAMAGE.
#

import atexit
import os
import subprocess
import glob
import re
import platform
import argparse
import yaml

# Path definitions
script_path: str = os.path.realpath(__file__)
script_dir: str = os.path.dirname(script_path)
repo_dir: str = os.path.dirname(script_dir)
gsdk_dir: str = os.path.join(repo_dir, "third_party", "silabs", "gecko_sdk")

# Utility functions

# Print a command and run it
def run_cmd(cmd: list[str]):
    print(">>>", " ".join(cmd))
    subprocess.run(cmd)

# Create srec files for all executables in a directory
def create_srec(directory: str):
    executable_flag = []
    if platform.system() == 'Linux':
        executable_flag = ['-executable']
    elif platform.system() == 'Darwin':
        executable_flag = ['-perm', '+111']

    run_cmd(['find', directory, '-type', 'f'] + executable_flag + ['-not', '-name', '*.*', '-exec', 'arm-none-eabi-objcopy', '-O', 'srec', '{}', '{}.s37', ';', '-exec', 'ls', '-alh', '{}', '{}.s37', ';'])


def efr32_get_board_slcc(board: str) -> str:
    """
    Gets the latest revision .slcc file for an efr32 board
    Args:
        board (str): efr32 board
    Returns:
        str: path to the board's .slcc file
    """

    # Find component file in "GSDK/hardware/board/component" for latest revision of board
    #   Some boards have multiple revisions, so we need to find the latest one
    #   Boards with multiple revisions have a naming convention like:
    #     - brd4311a_a01.slcc
    #     - brd4311a_a02.slcc
    #     - brd4311a_a03.slcc
    board_slcc = sorted(glob.glob(f"{gsdk_dir}/hardware/board/component/{board}*"))[-1]
    return board_slcc


def efr32_get_platform(board: str) -> str:
    """
    Gets the platform for an efr32 board
    Args:
        board (str): efr32 board
    Returns:
        str: platform name
    """

    # Regex for parsing efr32 device names
    efr32_device_regex = r''
    efr32_device_regex += r'(efr32)*'                             # Group 1 - efr32 (optional)
    efr32_device_regex += r'([a-zA-Z]{2})'                        # Group 2 - mg, bg, xg (product line)
    efr32_device_regex += r'(m)*'                                 # Group 3 - m (optional, modules only)
    efr32_device_regex += r'(\d{1,2})\d{0,1}'                     # Group 4 - 1, 12, 13, 21, 24, 210, 240 etc (series and configuration)
    efr32_device_regex += r'([a-zA-Z]{1})'                        # Group 5 - a, b, c, p, v (revision)
    efr32_device_regex += r'([a-zA-Z]{0,1}\d{1,3})'               # Group 6 - xxx, a32, 032
    efr32_device_regex += r'(f\d{1,})*'                           # Group 7 - fXXX (flash size)
    efr32_device_regex += r'([a-zA-Z]{2,3})*'                     # Group 8 - im, gl, gm, jia, vna, etc
    efr32_device_regex += r'(f\d{1,})*'                           # Group 9 - 32, 40, 48, 68, 125
    efr32_device_regex += r'.*'                                   # Rest of line

    # Find component file for latest revision of board
    board_slcc = efr32_get_board_slcc(board)

    # Determine board's platform and exit if unsupported
    platform: str = None
    with open(board_slcc, 'r') as file:
        for line in file:
            if 'board:device:' in line:
                platform = re.search(efr32_device_regex, re.escape(line))
                if platform:
                    platform = f"efr32{platform.group(2)}{platform.group(4)}"
                    break
    if not platform:
        print("Error parsing platform")
        exit(3)

    return platform


def efr32_get_platforms():
    """
    Gets a list of all efr32 platforms
    Returns:
        list: list of platform names
    """

    platform_dir = os.path.join(repo_dir, "src")
    platforms = [name for name in os.listdir(platform_dir) if os.path.isdir(os.path.join(platform_dir, name)) and "efr32" in name]
    platforms.sort()
    return platforms


def efr32_check_platform(platform):
    """
    Checks if a platform is valid for efr32
    Args:
        platform (str): platform name
    Returns:
        bool: True if platform is valid, False otherwise
    """
    platforms = efr32_get_platforms()
    if platform in platforms:
        return True
    else:
        print("\n\nERROR: Invalid platform")
        print("Valid platforms:")
        for p in platforms:
            print(" -", p)
        return False


# Pre-build checks
def check_git_lfs_installed():
    try:
        subprocess.check_output(["git", "lfs"])
    except subprocess.CalledProcessError:
        print("ERROR: Git LFS is not installed")
        print("Please run './script/bootstrap packages' to install it")
        exit(3)

def initialize_git_lfs():
    git_dir = os.path.join(gsdk_dir, ".git")
    pre_push_hook = os.path.join(git_dir, "hooks", "pre-push")
    if not os.path.isfile(pre_push_hook):
        subprocess.run(["git", "-C", gsdk_dir, "lfs", "install"])

def initialize_gsdk_submodule():
    subprocess.run(["git", "submodule", "update", "--init", gsdk_dir])
    subprocess.run(["git", "-C", gsdk_dir, "lfs", "pull"])

# Build functions


def generate_required_platform_libs(target: str):
    '''
    Generate the platform libs and related libs for a given target
    Args:
        target (str): target name
    '''
    map_target_to_slcp = {
        "ot-rcp-uart": repo_dir + "/slc/platform_projects/openthread-efr32-rcp-uart.slcp",
        "ot-rcp-spi":  repo_dir + "/slc/platform_projects/openthread-efr32-rcp-spi.slcp",
        "ot-cli-ftd":  repo_dir + "/slc/platform_projects/openthread-efr32-soc.slcp",
        "ot-cli-mtd":  repo_dir + "/slc/platform_projects/openthread-efr32-soc.slcp",
        "ot-ncp-ftd":  repo_dir + "/slc/platform_projects/openthread-efr32-soc.slcp",
        "ot-ncp-mtd":  repo_dir + "/slc/platform_projects/openthread-efr32-soc.slcp",
    }

    if target not in map_target_to_slcp:
        raise ValueError(f"No SLCP file associated with target: {target}")

    slcp = map_target_to_slcp.get(target)
    # Parse the project name from the slcp file
    with open(slcp, 'r') as file:
        slcp_data = yaml.safe_load(file)
        project_name = slcp_data.get('project_name')

    print(f"Generating {project_name} and {project_name}-mbedtls libs")
    generation_dir = os.path.join(slc_generated_projects_dir, project_name)
    run_cmd([repo_dir + "/script/generate",
            slcp,
            generation_dir,
            board])


def build_rcp_uart():
    print("Building ot-rcp (UART):")
    builddir = os.path.join(ot_cmake_build_dir, "openthread", "rcp_uart")
    os.makedirs(builddir, exist_ok=True)
    os.chdir(builddir)
    run_cmd(["cmake",
           "-GNinja",
           f"-DOT_PLATFORM_LIB_DIR={slc_generated_projects_dir}/rcp_uart",
           "-DOT_FTD=OFF",
           "-DOT_MTD=OFF",
           "-DOT_RCP=ON",
           "-DOT_APP_CLI=OFF",
           "-DOT_APP_NCP=OFF",
           "-DOT_APP_RCP=ON",
           "-DOT_COMPILE_WARNING_AS_ERROR=ON",
           *cmake_options,
           repo_dir,
           ])

    run_cmd(["ninja", "ot-rcp"])

    create_srec(builddir)
    os.chdir(repo_dir)

def build_rcp_spi():
    print("Building ot-rcp (SPI)")
    builddir = os.path.join(ot_cmake_build_dir, "openthread", "rcp_spi")
    os.makedirs(builddir, exist_ok=True)
    os.chdir(builddir)
    run_cmd(["cmake",
                    "-GNinja",
                    f"-DOT_PLATFORM_LIB_DIR={slc_generated_projects_dir}/rcp_spi",
                    "-DOT_FTD=OFF",
                    "-DOT_MTD=OFF",
                    "-DOT_RCP=ON",
                    "-DOT_APP_CLI=OFF",
                    "-DOT_APP_NCP=OFF",
                    "-DOT_APP_RCP=ON",
                    "-DOT_COMPILE_WARNING_AS_ERROR=ON",
                    "-DOT_NCP_SPI=ON",
                    *cmake_options,
                    repo_dir,
                    ])
    run_cmd(["ninja", "ot-rcp"])
    create_srec(builddir)
    os.chdir(repo_dir)

def build_soc():
    print("Building SoC apps:")
    for target in soc_targets:
        print(" -", target)

    builddir = os.path.join(ot_cmake_build_dir, "openthread", "soc")
    os.makedirs(builddir, exist_ok=True)
    os.chdir(builddir)

    # Check if any of the targets are ftd, mtd, or rcp
    ot_ftd = "ON" if any(re.match(".*-ftd", target) for target in soc_targets) else "OFF"
    ot_mtd = "ON" if any(re.match(".*-mtd", target) for target in soc_targets) else "OFF"

    # Check if any of the targets are ot-cli-*, ot-ncp-*, or ot-rcp.*
    ot_app_cli = "ON" if any(re.match("ot-cli-.*", target) for target in soc_targets) else "OFF"
    ot_app_ncp = "ON" if any(re.match("ot-ncp-.*", target) for target in soc_targets) else "OFF"

    run_cmd(["cmake",
                    "-GNinja",
                    f"-DOT_PLATFORM_LIB_DIR={slc_generated_projects_dir}/soc",
                    f"-DOT_FTD={ot_ftd}",
                    f"-DOT_MTD={ot_mtd}",
                    "-DOT_RCP=OFF",
                    f"-DOT_APP_CLI={ot_app_cli}",
                    f"-DOT_APP_NCP={ot_app_ncp}",
                    "-DOT_APP_RCP=OFF",
                    "-DOT_COMPILE_WARNING_AS_ERROR=ON",
                    *cmake_options,
                    repo_dir,
                    ])
    run_cmd(["ninja"] + soc_targets)
    create_srec(builddir)
    os.chdir(repo_dir)

def main():
    # Pre-build checks
    check_git_lfs_installed()
    initialize_git_lfs()
    initialize_gsdk_submodule()

    # Generate the platform libs and related libs
    if not skip_generation:
        for target in rcp_targets + soc_targets:
            generate_required_platform_libs(target)

    # Build ot-rcp targets
    if "ot-rcp-uart" in rcp_targets:
        build_rcp_uart()

    if "ot-rcp-spi" in rcp_targets:
        build_rcp_spi()

    # Build soc targets
    if soc_targets:
        build_soc()

    # Build silabs apps
    if not skip_silabs_apps:
        subprocess.run([repo_dir + "/script/build_example_apps", board])

# Cleanup tasks
def cleanup():
    # Placeholder for any cleanup tasks
    pass


if __name__ == "__main__":
    atexit.register(cleanup)

    # Parse args
    parser = argparse.ArgumentParser(description="Build script for OpenThread EFR32")
    parser.add_argument("board", help="Board name")
    parser.add_argument("--skip-generation", action="store_true", help="Skip generation of platform libs")
    parser.add_argument("--skip-silabs-apps", action="store_true", help="Skip building of Silabs apps")
    parser.add_argument("--vendor-extension", type=str, help="Path to a Vendor SLC extension")

    # Parse any remaining args as cmake args
    parser.add_argument("cmake_args", nargs=argparse.REMAINDER, help="Additional CMake arguments")

    args = parser.parse_args()
    board: str = args.board
    skip_generation: bool = args.skip_generation
    skip_silabs_apps: bool = args.skip_silabs_apps
    vendor_extension: str = args.vendor_extension

    if vendor_extension:
        print("Vendor extension is not supported yet")
        # TODO: Implement vendor extension support
        exit(3)

    # Parse efr32 platform for the selected board
    efr32_platform = efr32_get_platform(board)

    # Path definitions
    global ot_cmake_build_dir
    global slc_generated_projects_dir
    ot_cmake_build_dir = os.environ.get("OT_CMAKE_BUILD_DIR", os.path.join(repo_dir, "build", board))
    slc_generated_projects_dir = os.path.join(ot_cmake_build_dir, "slc")

    # Define list of targets to build
    ot_cmake_ninja_target = os.environ.get("OT_CMAKE_NINJA_TARGET", "").split()
    if not ot_cmake_ninja_target:
        if efr32_platform == "efr32mg1":
            ot_cmake_ninja_target = ["ot-rcp-uart"]
            skip_silabs_apps = True
        elif efr32_platform in ["efr32mg12", "efr32mg13", "efr32mg21", "efr32mg24"]:
            ot_cmake_ninja_target = ["ot-rcp-uart", "ot-rcp-spi", "ot-cli-ftd", "ot-cli-mtd", "ot-ncp-ftd", "ot-ncp-mtd"]

    global rcp_targets
    global soc_targets
    rcp_targets: list[str] = []
    soc_targets: list[str] = []
    for target in ot_cmake_ninja_target:
        if target.startswith("ot-rcp-"):
            rcp_targets.append(target)
        else:
            soc_targets.append(target)

    global cmake_options
    cmake_options = [
        "-DCMAKE_BUILD_TYPE=Release",
        "-DOT_DIAGNOSTIC=ON",
        "-DOT_EXTERNAL_HEAP=ON",
        "-DOT_SLAAC=ON",
        "-DEFR32_PLATFORM=" + efr32_platform,
        "-DBOARD=" + board,
        f"-DCMAKE_TOOLCHAIN_FILE=src/{efr32_platform}/arm-none-eabi.cmake",
        "--graphviz=graph.dot",
    ]
    # Add any additional cmake args
    cmake_options += args.cmake_args


    main()
