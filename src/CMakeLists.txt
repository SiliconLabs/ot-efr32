#
#  Copyright (c) 2021, The OpenThread Authors.
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

include(${PROJECT_SOURCE_DIR}/third_party/silabs/cmake/utility.cmake)
include(${PROJECT_SOURCE_DIR}/third_party/silabs/cmake/includes.cmake)
include(${PROJECT_SOURCE_DIR}/third_party/silabs/cmake/imported_libs.cmake)


# ==============================================================================
# Verify board is supported
# ==============================================================================
get_board_device()

list(APPEND OT_PLATFORM_DEFINES "${MCU}")
set(OT_PLATFORM_DEFINES ${OT_PLATFORM_DEFINES} PARENT_SCOPE)

# TODO: This will be removed when the configuration files in `src/efr32mg*/brd*/` are no longer manually generated and are generated as part of builds
if(NOT EXISTS "${PROJECT_SOURCE_DIR}/src/${PLATFORM_LOWERCASE}/${BOARD_LOWERCASE}")
    # Get list of boards supported for the platform
    file(GLOB platform_boards
            RELATIVE "${PROJECT_SOURCE_DIR}/src/${PLATFORM_LOWERCASE}/"
            "${PROJECT_SOURCE_DIR}/src/${PLATFORM_LOWERCASE}/brd*/")

    # Get first valid board to use as example
    list(GET platform_boards 0 valid_board)

    # Build error message
    set(error_message "
        MCU = ${MCU}
        Config folder ${PROJECT_SOURCE_DIR}/src/${PLATFORM_LOWERCASE}/${BOARD_LOWERCASE} does not exist
        BOARD=${BOARD} not supported.

        Please provide a value for BOARD variable e.g BOARD=${valid_board}.
        Currently supported:")
    foreach(board IN LISTS platform_boards)
        string(APPEND error_message "\n         - ${board}")
    endforeach()

    message(FATAL_ERROR "${error_message}")
endif()


# ==========================================================c====================
# Common sources and includes
# ==============================================================================
set(EFR32_COMMON_SOURCES
    src/alarm.c
    src/diag.c
    src/entropy.c
    src/fem-control.c
    src/flash.c
    src/ieee802154mac.h
    src/logging.c
    src/mbedtls_config.h
    src/memory.c
    src/misc.c
    src/openthread-core-efr32-config-check.h
    src/openthread-core-efr32-config.h
    src/platform-band.h
    src/platform-efr32.h
    src/radio.c
    src/rail_config.h
    src/startup-gcc.c
    src/system.c
    src/uart.c
)

set(EFR32_INCLUDES
    ${CMAKE_CURRENT_SOURCE_DIR}/src
    ${CMAKE_CURRENT_SOURCE_DIR}/${EFR32_PLATFORM}/crypto
    ${CMAKE_CURRENT_SOURCE_DIR}/${EFR32_PLATFORM}/${BOARD_LOWERCASE}
    ${PROJECT_SOURCE_DIR}/third_party/silabs/rail_config
    ${SILABS_GSDK_INCLUDES}
    ${PROJECT_SOURCE_DIR}/openthread/examples/platforms
    ${PROJECT_SOURCE_DIR}/src/core
)

set(EFR32_CFLAGS
    -Wno-sign-compare
    -Wno-unused-parameter
    -Wno-missing-field-initializers
)

# ==============================================================================
# mbedtls
# ==============================================================================
if(NOT OT_EXTERNAL_MBEDTLS)
    message(FATAL_ERROR "OT_EXTERNAL_MBEDTLS is not set. Please include the define when running cmake\n\t-DOT_EXTERNAL_MBEDTLS=silabs-mbedtls")
else()
    list(APPEND OT_PLATFORM_DEFINES "MBEDTLS_CONFIG_FILE=\"mbedtls_config.h\"")
endif()
set(OT_PLATFORM_DEFINES ${OT_PLATFORM_DEFINES} PARENT_SCOPE)

if(PLATFORM_LOWERCASE MATCHES "^efr32mg2\\d*")
    list(APPEND OT_PUBLIC_INCLUDES
        "${SILABS_GSDK_DIR}/util/third_party/crypto/sl_component/se_manager/inc"
        "${SILABS_GSDK_DIR}/util/third_party/crypto/sl_component/se_manager/src"
    )
    set(OT_PUBLIC_INCLUDES ${OT_PUBLIC_INCLUDES} PARENT_SCOPE)
endif()

# ==============================================================================
# General variables
# ==============================================================================

# ==============================================================================
# Platform targets
# ==============================================================================
set(EFR32_COMMON_3RD_LIBS
    jlinkrtt
    ${OT_MBEDTLS}
)

include(${PLATFORM_LOWERCASE}/${PLATFORM_LOWERCASE}.cmake)

list(APPEND OT_PUBLIC_INCLUDES ${EFR32_INCLUDES})
set(OT_PUBLIC_INCLUDES ${OT_PUBLIC_INCLUDES} PARENT_SCOPE)

target_include_directories(ot-config INTERFACE ${OT_PUBLIC_INCLUDES})
target_compile_definitions(ot-config INTERFACE ${OT_PLATFORM_DEFINES})
