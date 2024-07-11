import os
import subprocess

# Bash definitions
script_path = os.path.realpath(__file__)
script_dir = os.path.dirname(script_path)
repo_dir = os.path.dirname(script_dir)

# Source files
efr32_definitions = os.path.join(repo_dir, "script", "efr32-definitions")
slc_cli = os.path.join(repo_dir, "script", "slc_cli")
util = os.path.join(repo_dir, "script", "util")

# OT options
OT_OPTIONS = [
    "-DCMAKE_BUILD_TYPE=Release",
    "-DOT_DIAGNOSTIC=ON",
    "-DOT_EXTERNAL_HEAP=ON",
    "-DOT_PING_SENDER=ON",
    "-DOT_SLAAC=ON"
]

def die(message):
    print(f" ** ERROR: {message}")
    exit(1)

def generate(slcp_file, generation_dir):
    if skip_generation:
        return

    print("=========================================================================================================")
    print(f"Generating {slcp_file}")
    print("=========================================================================================================")

    subprocess.run([os.path.join(repo_dir, "script", "generate"), slcp_file, generation_dir, board], check=True)

def build_example_app(example_app_ninja_target, slcp_file):
    # Parse the project name from the slcp file
    if not os.path.isfile(slcp_file):
        die(f"SLCP file not found: {slcp_file}")
    with open(slcp_file, "r") as f:
        ot_platform_lib = f.read().split("project_name: ")[1].strip()

    # Generate the platform lib and related libs
    generated_ot_platform_lib_dir = os.path.join(slc_generated_projects_dir, ot_platform_lib)
    generate(slcp_file, generated_ot_platform_lib_dir)

    # Create the build directory
    builddir = os.path.join(OT_CMAKE_BUILD_DIR, "examples", example_app_ninja_target)
    os.makedirs(builddir, exist_ok=True)
    os.chdir(builddir)

    # Configure and build the example app
    cmake_args = [
        "-GNinja",
        "-DOT_COMPILE_WARNING_AS_ERROR=ON",
        f"-DOT_PLATFORM_LIB={ot_platform_lib}",
        f"-DOT_PLATFORM_LIB_DIR={generated_ot_platform_lib_dir}",
        f"-DOT_EXTERNAL_MBEDTLS={ot_platform_lib}-mbedtls",
        "-DOT_APP_CLI=OFF",
        "-DOT_APP_NCP=OFF",
        "-DOT_APP_RCP=OFF",
        *OT_OPTIONS,
        repo_dir
    ]
    subprocess.run(["cmake"] + cmake_args, check=True)
    subprocess.run(["ninja", example_app_ninja_target], check=True)

    create_srec(builddir)
    os.chdir(repo_dir)

def get_associated_cmake_app_option(cmake_executable):
    if cmake_executable == "sleepy-demo-ftd":
        return "EFR32_APP_SLEEPY_DEMO_FTD"
    elif cmake_executable == "sleepy-demo-mtd":
        return "EFR32_APP_SLEEPY_DEMO_MTD"
    elif cmake_executable == "sleepy-demo-ssed":
        return "EFR32_APP_SLEEPY_DEMO_SSED"
    else:
        die(f"Unknown CMake executable: {cmake_executable}")

def get_associated_slcp(cmake_executable):
    if cmake_executable == "sleepy-demo-ftd":
        return os.path.join(repo_dir, "slc", "platform_projects", "openthread-efr32-soc-with-buttons.slcp")
    elif cmake_executable == "sleepy-demo-mtd":
        return os.path.join(repo_dir, "slc", "platform_projects", "openthread-efr32-soc-with-buttons-power-manager.slcp")
    elif cmake_executable == "sleepy-demo-ssed":
        return os.path.join(repo_dir, "slc", "platform_projects", "openthread-efr32-soc-with-buttons-power-manager-csl.slcp")
    else:
        die(f"Unknown CMake executable: {cmake_executable}")

def main():
    usage = "usage: build_example_apps.py [-h] [--skip-silabs-apps] <brdXXXXy> [-D<OT_XXXX=ON> -D<OT_YYYY=OFF>]"

    skip_generation = False

    # Parse flags
    args = sys.argv[1:]
    while args:
        arg = args.pop(0)
        if arg == "--skip-generation":
            print("\n\nSkipping SLC generation...\n\n")
            skip_generation = True
        elif arg == "-h":
            print(usage)
            exit(0)
        else:
            break

    # Parse board
    board = args.pop(0).lower() if args else None

    # Find component file for latest revision of board
    board_slcc = efr32_get_board_slcc(board)

    # Determine board's platform and exit if unsupported
    platform = None
    with open(board_slcc, "r") as f:
        for line in f:
            if line.startswith("board:device:"):
                platform = line.split(":")[2].replace(efr32_device_regex, "efr32\\2\\4")
                break
    if not platform:
        die("Error parsing platform")
    if not efr32_check_platform(platform):
        die(f"Unsupported platform {platform}")

    options = [*OT_OPTIONS]
    options.append(f"-DCMAKE_TOOLCHAIN_FILE=src/{platform}/arm-none-eabi.cmake")

    # Find slc-cli installation
    slc_init()

    options.extend(args)
    OT_CMAKE_BUILD_DIR = os.path.join(repo_dir, "build", board)
    slc_generated_projects_dir = os.path.join(OT_CMAKE_BUILD_DIR, "slc")

    # If no target is specified, build all targets
    if not OT_CMAKE_NINJA_TARGET:
        OT_CMAKE_NINJA_TARGET = ["sleepy-demo-ftd", "sleepy-demo-mtd", "sleepy-demo-ssed"]

    # Build the example apps
    for target in OT_CMAKE_NINJA_TARGET:
        build_example_app(target, get_associated_slcp(target), options + [f"-D{get_associated_cmake_app_option(target)}=ON"])

    # List the built binaries
    for target in OT_CMAKE_NINJA_TARGET:
        target_dir = os.path.join(OT_CMAKE_BUILD_DIR, "examples", target)
        if os.path.isdir(target_dir):
            for file in os.listdir(os.path.join(target_dir, "bin")):
                print(os.path.join(target_dir, "bin", file))

if __name__ == "__main__":
    main()
