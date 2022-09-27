#include "sl_event_handler.h"

#include "em_chip.h"
#include "sl_device_init_nvic.h"
#include "sl_board_init.h"
#include "sl_device_init_dcdc.h"
#include "sl_device_init_hfxo.h"
#include "sl_device_init_lfxo.h"
#include "sl_device_init_clocks.h"
#include "sl_device_init_emu.h"
#include "pa_conversions_efr32.h"
#include "sl_rail_util_pti.h"
#include "sl_rail_util_rssi.h"
#include "sl_board_control.h"
#include "platform-efr32.h"
#include "sl_sleeptimer.h"
#include "sl_debug_swo.h"
#include "gpiointerrupt.h"
#include "sl_mbedtls.h"
#include "sl_mpu.h"
#include "nvm3_default.h"
#include "sl_ot_init.h"
#include "sl_uartdrv_instances.h"
#include "sl_cos.h"

void sl_platform_init(void)
{
  CHIP_Init();
  sl_device_init_nvic();
  sl_board_preinit();
  sl_device_init_dcdc();
  sl_device_init_hfxo();
  sl_device_init_lfxo();
  sl_device_init_clocks();
  sl_device_init_emu();
  sl_board_init();
  nvm3_initDefault();
}

void sl_driver_init(void)
{
  sl_debug_swo_init();
  GPIOINT_Init();
  sl_uartdrv_init_instances();
  sl_cos_send_config();
}

void sl_service_init(void)
{
  sl_board_configure_vcom();
  sl_sleeptimer_init();
  sl_mbedtls_init();
  sl_mpu_disable_execute_from_ram();
}

void sl_stack_init(void)
{
  sl_rail_util_pa_init();
  sl_rail_util_pti_init();
  sl_rail_util_rssi_init();
  sl_ot_sys_init();
}

void sl_internal_app_init(void)
{
  sl_ot_init();
}

void sl_platform_process_action(void)
{
}

void sl_service_process_action(void)
{
}

void sl_stack_process_action(void)
{
}

void sl_internal_app_process_action(void)
{
}

