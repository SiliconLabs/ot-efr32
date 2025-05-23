/*
 *  Copyright (c) 2024, The OpenThread Authors.
 *  All rights reserved.
 *
 *  Redistribution and use in source and binary forms, with or without
 *  modification, are permitted provided that the following conditions are met:
 *  1. Redistributions of source code must retain the above copyright
 *     notice, this list of conditions and the following disclaimer.
 *  2. Redistributions in binary form must reproduce the above copyright
 *     notice, this list of conditions and the following disclaimer in the
 *     documentation and/or other materials provided with the distribution.
 *  3. Neither the name of the copyright holder nor the
 *     names of its contributors may be used to endorse or promote products
 *     derived from this software without specific prior written permission.
 *
 *  THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
 *  AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
 *  IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
 *  ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE
 *  LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
 *  CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
 *  SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
 *  INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
 *  CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
 *  ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
 *  POSSIBILITY OF SUCH DAMAGE.
 */

/**
 * @file
 *   This file includes the platform-specific initializers.
 *
 */

#ifndef PLATFORM_EFR32_H_
#define PLATFORM_EFR32_H_

#ifdef __cplusplus
extern "C" {
#endif

#include <openthread/instance.h>

#include "em_device.h"
#if defined(_SILICON_LABS_32B_SERIES_2)
#include "em_system.h"
#else
#include "sl_hal_system.h"
#endif

#include "rail.h"

#include "alarm.h"
#include "uart.h"

// Global OpenThread instance structure
extern otInstance *sInstance;

#ifdef SL_COMPONENT_CATALOG_PRESENT
#include "sl_component_catalog.h"
#endif // SL_COMPONENT_CATALOG_PRESENT

#ifndef SL_CATALOG_KERNEL_PRESENT
#define sl_ot_rtos_task_can_access_pal() (true)
#else
#include "sl_ot_rtos_adaptation.h"
#endif

// Global reference to rail handle
#ifndef SL_CATALOG_RAIL_MULTIPLEXER_PRESENT
#define gRailHandle emPhyRailHandle // use gRailHandle in the OpenThread PAL.
#endif

extern RAIL_Handle_t gRailHandle; // coex needs the emPhyRailHandle symbol.

/**
 * This function performs all platform-specific initialization of
 * OpenThread's drivers.
 *
 */
void sl_ot_sys_init(void);

/**
 * This function initializes the radio service used by OpenThead.
 *
 */
void efr32RadioInit(void);

/**
 * This function deinitializes the radio service used by OpenThead.
 *
 */
void efr32RadioDeinit(void);

/**
 * This function performs radio driver processing.
 *
 * @param[in]  aInstance  The OpenThread instance structure.
 *
 */
void efr32RadioProcess(otInstance *aInstance);

/**
 * This function performs CPC driver processing.
 *
 */
void efr32CpcProcess(void);

/**
 * This function performs SPI driver processing.
 *
 */
void efr32SpiProcess(void);

/**
 * Initialization of Misc module.
 *
 */
void efr32MiscInit(void);

/**
 * Initialization of ADC module for random number generator.
 *
 */
void efr32RandomInit(void);

/**
 * Initialization of Logger driver.
 *
 */
void efr32LogInit(void);

/**
 * Deinitialization of Logger driver.
 *
 */
void efr32LogDeinit(void);

/**
 * Print reset info.
 *
 */
void efr32PrintResetInfo(void);

/**
 * Set 802.15.4 CCA mode
 *
 * A call to this function should be made after RAIL has been
 * initialized and a valid handle is available. On platforms that
 * don't support different CCA modes, a call to this function with
 * non-Default CCA mode (i.e. with any value except
 * RAIL_IEEE802154_CCA_MODE_RSSI) will return a failure.
 *
 * @param[in] aMode Mode of CCA operation.
 * @return RAIL Status code indicating success of the function call.
 */
RAIL_Status_t efr32RadioSetCcaMode(uint8_t aMode);

/**
 * This callback is used to check if is safe to put the EFR32 into a
 * low energy sleep mode.
 *
 * The callback should return true if it is ok to enter sleep mode.
 * Note that the callback must add an EM1 requirement if it intends
 * to idle (EM1) instead of entering a deep sleep (EM2) mode.
 */

bool efr32AllowSleepCallback(void);

/**
 * Load the channel configurations.
 *
 * @param[in]  aChannel   The radio channel.
 * @param[in]  aTxPower   The radio transmit power in dBm.
 *
 * @retval OT_ERROR_NONE         Successfully enabled/disabled .
 * @retval OT_ERROR_INVALID_ARGS Invalid channel.
 *
 */
otError efr32RadioLoadChannelConfig(uint8_t aChannel, int8_t aTxPower);

otError railStatusToOtError(RAIL_Status_t status);

/**
 * This function performs Serial processing.
 *
 */
void efr32SerialProcess(void);

#ifdef __cplusplus
}
#endif

#endif // PLATFORM_EFR32_H_
