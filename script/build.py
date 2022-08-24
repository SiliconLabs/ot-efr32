#!/usr/bin/env python3

import argparse
from glob import glob
import os
import logging
import pathlib
import shutil
import time
from typing import Type, TypedDict
from zipfile import ZipFile
from script.efr32 import Board
from script.slc import GeneratedProject, SlcInstallation, SlcProjectTemplate
from script.util import execute_and_log

# ==============================================================================
# System paths
# ==============================================================================
script_dir = os.path.dirname(os.path.realpath(__file__))
repo_dir = os.path.realpath(f"{script_dir}/../")
sdk_dir = os.path.realpath(f"{repo_dir}/third_party/silabs/gecko_sdk")

# ==============================================================================
# Configs for GeneratedProjects
# ==============================================================================


class GeneratedProjectConfig(TypedDict):
    # The name of this config
    name: str

    # The SLCP for this this target
    project: SlcProjectTemplate

    # The export templates to use
    export_templates: pathlib.Path

    # dict of files to rename: dict[src, dest]
    rename_output_files: dict[str, str]

    # list of files to remove
    remove_output_files: list[str]


generated_projects_configs: dict[str, GeneratedProjectConfig] = {
    "soc/platform": GeneratedProjectConfig(
        name="soc/platform",
        project=SlcProjectTemplate(
            f"{repo_dir}/src/platform_projects/openthread-efr32-soc.slcp"),
        export_templates=f"{repo_dir}/third_party/silabs/slc/exporter_templates/platform_library",
        # rename_templates={
        #     "openthread-efr32-xxx.cmake.jinja": "custom.Makefile",
        #     "openthread-efr32-xxx-sdk.cmake.jinja": "custom.project.mak"
        # },
        rename_output_files={
            "openthread-efr32-soc.Makefile": "CMakeLists.txt",
            "openthread-efr32-soc.project.mak": "openthread-efr32-soc-sdk.cmake"
        }
    ),
    "soc/mbedtls": GeneratedProjectConfig(
        name="soc/mbedtls",
        project=SlcProjectTemplate(
            f"{repo_dir}/src/platform_projects/openthread-efr32-soc.slcp"),
        export_templates=f"{repo_dir}/third_party/silabs/slc/exporter_templates/mbedtls",
        rename_output_files={
            "openthread-efr32-soc.Makefile": "CMakeLists.txt",
        },
        remove_output_files=[
            "openthread-efr32-soc.project.mak",
            "autogen/",
            "config/",
        ]
    ),
    "rcp/platform": GeneratedProjectConfig(
        name="rcp/platform",
        project=SlcProjectTemplate(
            f"{repo_dir}/src/platform_projects/openthread-efr32-rcp.slcp"),
        export_templates=f"{repo_dir}/third_party/silabs/slc/exporter_templates/platform_library",
        # rename_templates={
        #     "openthread-efr32-xxx.cmake.jinja": "custom.Makefile",
        #     "openthread-efr32-xxx-sdk.cmake.jinja": "custom.project.mak"
        # },
        rename_output_files={
            "openthread-efr32-rcp.Makefile": "CMakeLists.txt",
            "openthread-efr32-rcp.project.mak": "openthread-efr32-rcp-sdk.cmake"
        }
    ),
    "rcp/mbedtls": GeneratedProjectConfig(
        name="rcp/mbedtls",
        project=SlcProjectTemplate(
            f"{repo_dir}/src/platform_projects/openthread-efr32-rcp.slcp"),
        export_templates=f"{repo_dir}/third_party/silabs/slc/exporter_templates/mbedtls",
        rename_output_files={
            "openthread-efr32-rcp.Makefile": "CMakeLists.txt",
        },
        remove_output_files=[
            "openthread-efr32-rcp.project.mak",
            "autogen/",
            "config/",
        ]
    ),
    # "soc/platform-with-buttons-power-manager": {
    #     "project": SlcProjectTemplate(
    #         f"{repo_dir}/src/platform_projects/openthread-efr32-soc-with-buttons-power-manager.slcp"),
    #     # Where to generate this this project relative to the build_dir
    #     "export_destination": f"slc/soc/platform-with-buttons-power-manager",
    #     "export_templates": f"{repo_dir}/third_party/silabs/slc/exporter_templates/platform_library",
    #     "rename_output_files": {
    #         "openthread-efr32-soc-with-buttons-power-manager.Makefile": "CMakeLists.txt",
    #         "openthread-efr32-soc-with-buttons-power-manager.project.mak": "openthread-efr32-soc-with-buttons-power-manager-sdk.cmake"
    #     }
    # },
}


# ==============================================================================
# Functions
# ==============================================================================


def build(board: Board, targets: list[str], build_dir: str, slc: SlcInstallation) -> None:

    # Map a target to the GeneratedProjectConfig it depends on
    target_to_generated_project_config: dict[str, list[str]] = {
        "ot-cli-ftd":       [generated_projects_configs["soc/platform"], generated_projects_configs["soc/mbedtls"]],
        "ot-cli-mtd":       [generated_projects_configs["soc/platform"], generated_projects_configs["soc/mbedtls"]],
        "ot-ncp-ftd":       [generated_projects_configs["soc/platform"], generated_projects_configs["soc/mbedtls"]],
        "ot-ncp-mtd":       [generated_projects_configs["soc/platform"], generated_projects_configs["soc/mbedtls"]],
        "ot-rcp":           [generated_projects_configs["rcp/platform"], generated_projects_configs["rcp/mbedtls"]],
        # "sleepy-demo-ftd":  [generated_projects_configs["soc/platform"], generated_projects_configs["soc/mbedtls"]],
        # "sleepy-demo-mtd":  [generated_projects_configs["soc/platform"], generated_projects_configs["soc/mbedtls"]],
    }

    # Build set of slc projects
    needed_generated_project_configs: dict[str, GeneratedProject] = dict()
    for target in targets:
        if target not in target_to_generated_project_config:
            continue

        # Add each required GeneratedProject's config
        for config in target_to_generated_project_config[target]:

            # Skip any config we've already added
            if config["name"] in needed_generated_project_configs:
                pass

            needed_generated_project_configs[config["name"]] = GeneratedProject(
                **config,
                board=board,
                export_destination=f"{build_dir}/slc/{config['name']}",
                slc_executable=slc.executable
            )

            pass

    # Generate slc projects
    logging.info(f"Generating:")
    for name,project in needed_generated_project_configs.items():
        logging.info(f"- {name}: {project}")
        project.generate()

    # Generate ninja files
    OT_OPTIONS = [
        "-DCMAKE_BUILD_TYPE=Debug",
        "-DOT_DIAGNOSTIC=ON",
        "-DOT_EXTERNAL_HEAP=ON",
        "-DOT_SLAAC=ON",
    ]
    cmake_flags = [
        "-DOT_COMPILE_WARNING_AS_ERROR=ON",
        f"-DCMAKE_TOOLCHAIN_FILE=src/{board.get_platform()}/arm-none-eabi.cmake",
        f"-DEFR32_PLATFORM={board.get_platform()}",
        f"-DBOARD={board}",
    ]

    # log file path
    timestamp = time.strftime("%Y-%m-%dT%H%M%S")
    build_log_file = f'{build_dir}/build_{timestamp}.log'

    cmake_cmd = ["cmake", "-GNinja"] + OT_OPTIONS + cmake_flags
    cmake_cmd.append(repo_dir)
    execute_and_log(cmake_cmd, build_log_file)
    ninja_cmd = ["ninja"] + targets
    execute_and_log(ninja_cmd, build_log_file)

    return


# ==============================================================================
# Main
# ==============================================================================
if __name__ == "__main__":
    logging.basicConfig(filename='build.log', level=logging.DEBUG)
    logging.getLogger().addHandler(logging.StreamHandler())

    parser = argparse.ArgumentParser()
    parser.add_argument("board", type=Board, help="EFR32 board")
    parser.add_argument("--skip-silabs-apps", action="store_true",
                        help="Skips generation and build of Silicon Labs apps (ex. sleepy-demo-ftd, sleepy-demo-mtd)")
    parser.add_argument("--skip-generation", action="store_true",
                        help="Skips slc-cli generation. This is usually helpful when iterating on changes that don't require template regeneration")
    parser.add_argument("--force-slc-installation", action="store_true",
                        help="Forces slc-cli to be downloaded to the path specified by env variable \'SLC_INSTALL_DIR\'")

    args = parser.parse_args()

    # Parse board
    board: Board = args.board
    assert board.device["family"] == "mg", f"{board} ({board.platform}) is not supported"

    skip_silabs_apps = args.skip_silabs_apps
    skip_generation = args.skip_generation
    force_slc_installation = args.force_slc_installation

    # Default OT CMake options
    ot_cmake_options = [
        "-DCMAKE_BUILD_TYPE=Debug",
        "-DOT_DIAGNOSTIC=ON",
        "-DOT_EXTERNAL_HEAP=ON",
        "-DOT_SLAAC=ON",
        # Platform-specific toolchain file
        f"-DCMAKE_TOOLCHAIN_FILE=src/{board.get_platform()}/arm-none-eabi.cmake",
        f"-DEFR32_PLATFORM=\"{board.platform}\"",
        f"-DBOARD={board}",
    ]

    ot_cmake_ninja_targets = ["ot-rcp"]
    # TODO: We can probably parse for RAM/FLASH sizes and figure out what can fit on each platform
    if board.platform != "efr32mg1":
        ot_cmake_ninja_targets += [
            "ot-cli-ftd", "ot-cli-mtd", "ot-ncp-ftd", "ot-ncp-mtd"]

        # if not skip_silabs_apps:
        #     ot_cmake_ninja_targets += ["sleepy-demo-ftd", "sleepy-demo-mtd"]

    # Initialize slc-cli installation
    global slc
    slc = SlcInstallation(force_slc_installation)

    # Get build_dir from env variables
    build_dir = os.environ.get(
        "OT_CMAKE_BUILD_DIR") or f"{repo_dir}/build/{board}"
    pathlib.Path(build_dir).mkdir(parents=True, exist_ok=True)

    build(board, ot_cmake_ninja_targets, build_dir=build_dir, slc=slc)
