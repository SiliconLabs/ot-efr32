####################################################################
# Automatically-generated file. Do not edit!                       #
# CMake Version 1                                                  #
####################################################################
#
#  Copyright (c) 2022, The OpenThread Authors.
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
include(openthread-efr32-rcp-sdk.cmake)

# ==============================================================================
# Platform library
# ==============================================================================
add_library(openthread-efr32-rcp
    $<TARGET_OBJECTS:openthread-platform-utils>
)

# Interface lib for sharing efr32 config to relevant targets
add_library(openthread-efr32-rcp-config INTERFACE)

# Define RCP specific libraries
set(OT_PLATFORM_LIB_RCP openthread-efr32-rcp)
set(OT_MBEDTLS_RCP silabs-mbedtls-rcp)

set_target_properties(openthread-efr32-rcp
    PROPERTIES
        C_STANDARD 99
        CXX_STANDARD 11
)

# ==============================================================================
# Includes
# ==============================================================================
target_include_directories(ot-config INTERFACE
    ${SILABS_GSDK_DIR}/platform/Device/SiliconLabs/EFR32MG12P/Include
    ${SILABS_GSDK_DIR}/platform/common/inc
    ${SILABS_GSDK_DIR}/hardware/board/inc
    ${SILABS_GSDK_DIR}/platform/CMSIS/Core/Include
    ${SILABS_GSDK_DIR}/hardware/driver/configuration_over_swo/inc
    ${SILABS_GSDK_DIR}/platform/driver/debug/inc
    ${SILABS_GSDK_DIR}/platform/service/device_init/inc
    ${SILABS_GSDK_DIR}/platform/emdrv/dmadrv/inc
    ${SILABS_GSDK_DIR}/platform/emdrv/common/inc
    ${SILABS_GSDK_DIR}/platform/emlib/inc
    ${SILABS_GSDK_DIR}/platform/emdrv/gpiointerrupt/inc
    ${SILABS_GSDK_DIR}/util/third_party/crypto/mbedtls/include
    ${SILABS_GSDK_DIR}/util/third_party/crypto/mbedtls/library
    ${SILABS_GSDK_DIR}/util/third_party/crypto/sl_component/sl_mbedtls_support/config
    ${SILABS_GSDK_DIR}/util/third_party/crypto/sl_component/sl_mbedtls_support/inc
    ${SILABS_GSDK_DIR}/platform/service/mpu/inc
    ${SILABS_GSDK_DIR}/hardware/driver/mx25_flash_shutdown/inc/sl_mx25_flash_shutdown_usart
    ${SILABS_GSDK_DIR}/platform/emdrv/nvm3/inc
    ${PROJECT_SOURCE_DIR}/openthread/examples/platforms
    ${PROJECT_SOURCE_DIR}/openthread/examples/platforms/utils
    ${PROJECT_SOURCE_DIR}/src/src
    ${SILABS_GSDK_DIR}/util/third_party/crypto/sl_component/sl_psa_driver/inc
    ${SILABS_GSDK_DIR}/util/third_party/crypto/sl_component/sl_psa_driver/inc/public
    ${SILABS_GSDK_DIR}/platform/radio/rail_lib/common
    ${SILABS_GSDK_DIR}/platform/radio/rail_lib/protocol/ble
    ${SILABS_GSDK_DIR}/platform/radio/rail_lib/protocol/ieee802154
    ${SILABS_GSDK_DIR}/platform/radio/rail_lib/protocol/zwave
    ${SILABS_GSDK_DIR}/platform/radio/rail_lib/chip/efr32/efr32xg1x
    ${SILABS_GSDK_DIR}/platform/radio/rail_lib/plugin/pa-conversions
    ${SILABS_GSDK_DIR}/platform/radio/rail_lib/plugin/pa-conversions/efr32xg1x
    ${SILABS_GSDK_DIR}/platform/radio/rail_lib/plugin/rail_util_pti
    ${SILABS_GSDK_DIR}/platform/radio/rail_lib/plugin/rail_util_rssi
    ${SILABS_GSDK_DIR}/util/third_party/segger/systemview/SEGGER
    ${SILABS_GSDK_DIR}/util/silicon_labs/silabs_core/memory_manager
    ${SILABS_GSDK_DIR}/platform/common/toolchain/inc
    ${SILABS_GSDK_DIR}/platform/service/system/inc
    ${SILABS_GSDK_DIR}/platform/service/sleeptimer/inc
    ${SILABS_GSDK_DIR}/util/third_party/crypto/sl_component/sl_protocol_crypto/src
    ${SILABS_GSDK_DIR}/platform/emdrv/uartdrv/inc
    ${SILABS_GSDK_DIR}/platform/service/udelay/inc
)

target_include_directories(openthread-efr32-rcp-config INTERFACE
    autogen
    config
)

target_link_libraries(openthread-radio PUBLIC openthread-efr32-rcp-config)

target_include_directories(openthread-efr32-rcp PRIVATE
    ${OT_PUBLIC_INCLUDES}
)

# ==============================================================================
# Sources
# ==============================================================================
target_sources(openthread-efr32-rcp PRIVATE
    ${PROJECT_SOURCE_DIR}/src/src/alarm.c
    ${PROJECT_SOURCE_DIR}/src/src/board_config.h
    ${PROJECT_SOURCE_DIR}/src/src/crypto.c
    ${PROJECT_SOURCE_DIR}/src/src/diag.c
    ${PROJECT_SOURCE_DIR}/src/src/entropy.c
    ${PROJECT_SOURCE_DIR}/src/src/flash.c
    ${PROJECT_SOURCE_DIR}/src/src/ieee802154-packet-utils.cpp
    ${PROJECT_SOURCE_DIR}/src/src/ieee802154-packet-utils.hpp
    ${PROJECT_SOURCE_DIR}/src/src/ieee802154mac.h
    ${PROJECT_SOURCE_DIR}/src/src/logging.c
    ${PROJECT_SOURCE_DIR}/src/src/memory.c
    ${PROJECT_SOURCE_DIR}/src/src/misc.c
    ${PROJECT_SOURCE_DIR}/src/src/openthread-core-efr32-config-check.h
    ${PROJECT_SOURCE_DIR}/src/src/openthread-core-efr32-config.h
    ${PROJECT_SOURCE_DIR}/src/src/platform-band.h
    ${PROJECT_SOURCE_DIR}/src/src/platform-efr32.h
    ${PROJECT_SOURCE_DIR}/src/src/radio.c
    ${PROJECT_SOURCE_DIR}/src/src/rail_config.h
    ${PROJECT_SOURCE_DIR}/src/src/security_manager.c
    ${PROJECT_SOURCE_DIR}/src/src/security_manager.h
    ${PROJECT_SOURCE_DIR}/src/src/sl_openthread.h
    ${PROJECT_SOURCE_DIR}/src/src/sl_packet_utils.h
    ${PROJECT_SOURCE_DIR}/src/src/startup-gcc.c
    ${PROJECT_SOURCE_DIR}/src/src/system.c
    ${PROJECT_SOURCE_DIR}/src/src/uartdrv_uart.c
)

# ==============================================================================
# Compile definitions
# ==============================================================================
target_compile_definitions(ot-config INTERFACE
    EFR32MG12P432F1024GL125=1
    SL_BOARD_NAME="BRD4161A"
    SL_BOARD_REV="A03"
    SL_COMPONENT_CATALOG_PRESENT=1
    MBEDTLS_CONFIG_FILE=<mbedtls_config.h>
    OPENTHREAD_CONFIG_ENABLE_BUILTIN_MBEDTLS=0
    OPENTHREAD_CORE_CONFIG_PLATFORM_CHECK_FILE="openthread-core-efr32-config-check.h"
    OPENTHREAD_PROJECT_CORE_CONFIG_FILE="openthread-core-efr32-config.h"
    BUFFER_SIZE_DOWN=0
    BUFFER_SIZE_UP=768
    MBEDTLS_PSA_CRYPTO_CONFIG_FILE=<psa_crypto_config.h>
    SL_RAIL_LIB_MULTIPROTOCOL_SUPPORT=0
    SL_RAIL_UTIL_PA_CONFIG_HEADER=<sl_rail_util_pa_config.h>
    RTT_USE_ASM=0
    SEGGER_RTT_SECTION="SEGGER_RTT"
)

target_compile_definitions(openthread-efr32-rcp-config INTERFACE
    MBEDTLS_PSA_CRYPTO_CLIENT=1
)

target_compile_definitions(openthread-efr32-rcp PUBLIC 
        OPENTHREAD_COPROCESSOR=1
        OPENTHREAD_RADIO=1
)

target_compile_definitions(openthread-efr32-rcp-sdk PRIVATE 
        OPENTHREAD_COPROCESSOR=1
        OPENTHREAD_RADIO=1
)

target_compile_options(openthread-efr32-rcp PRIVATE 
    # GNU C flags
    $<$<COMPILE_LANG_AND_ID:C,GNU>:
        "SHELL:-mcpu=cortex-m4"
        "SHELL:-mthumb"
        "SHELL:-mfpu=fpv4-sp-d16"
        "SHELL:-mfloat-abi=softfp"
        "SHELL:-std=c99"
        "SHELL:-Wall"
        "SHELL:-Wextra"
        "SHELL:-Os"
        "SHELL:-fdata-sections"
        "SHELL:-ffunction-sections"
        "SHELL:-fomit-frame-pointer"
        "SHELL:-imacros sl_gcc_preinclude.h"
        "SHELL:-imacros sl_gcc_preinclude.h"
        "SHELL:--specs=nano.specs"
        "SHELL:-g"
    > 
)

# ==============================================================================
# Linking
# ==============================================================================
set(LD_FILE "${CMAKE_CURRENT_SOURCE_DIR}/autogen/linkerfile.ld")
set(openthread-efr32-rcp-sdk_location $<TARGET_FILE:openthread-efr32-rcp-sdk>)

target_link_libraries(openthread-efr32-rcp
    PUBLIC
        -lstdc++
        -lgcc
        -lc
        -lm
        -lnosys
        openthread-efr32-rcp-config

    PRIVATE
        -T${LD_FILE}
        -Wl,--gc-sections

        # The --whole-archive flags are necessary to resolve all symbols from the GSDK
        -Wl,--whole-archive ${openthread-efr32-rcp-sdk_location} -Wl,--no-whole-archive
        ot-config
)

target_link_options(openthread-efr32-rcp PRIVATE 
    -mcpu=cortex-m4
    -mthumb
    -mfpu=fpv4-sp-d16
    -mfloat-abi=softfp
    -Wl,--gc-sections
)

# ==============================================================================
# Static libraries from GSDK
# ==============================================================================
set(GSDK_LIBS
    "${SILABS_GSDK_DIR}/platform/emdrv/nvm3/lib/libnvm3_CM4_gcc.a"
    "${SILABS_GSDK_DIR}/protocol/openthread/libs/libsl_openthread_efr32mg1x_gcc.a"
    "${SILABS_GSDK_DIR}/platform/radio/rail_lib/autogen/librail_release/librail_efr32xg12_gcc_release.a"
)

# Import GSDK static libs and set a dependency on the GSDK library
# This will ensure proper linking order
foreach(lib_file ${GSDK_LIBS})
    # Parse lib name, stripping .a extension
    get_filename_component(lib_name ${lib_file} NAME_WE)
    set(imported_lib_name "silabs-${lib_name}")

    # Add as an IMPORTED lib
    add_library(${imported_lib_name} STATIC IMPORTED)
    set_target_properties(${imported_lib_name}
        PROPERTIES
            IMPORTED_LOCATION "${lib_file}"
            IMPORTED_LINK_INTERFACE_LIBRARIES openthread-efr32-rcp-sdk
    )
    target_link_libraries(openthread-efr32-rcp PUBLIC ${imported_lib_name})
endforeach()
