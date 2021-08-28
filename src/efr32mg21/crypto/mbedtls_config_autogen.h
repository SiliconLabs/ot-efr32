// This is an autogenerated config file, any changes to this file will be overwritten

#ifndef MBEDTLS_CONFIG_AUTOGEN_H
#define MBEDTLS_CONFIG_AUTOGEN_H

#define MBEDTLS_ECP_MAX_BITS 256

#define MBEDTLS_MPI_MAX_SIZE 32

#define MBEDTLS_AES_C
#define MBEDTLS_ASN1_PARSE_C
#define MBEDTLS_ASN1_WRITE_C
#define MBEDTLS_BASE64_C
#define MBEDTLS_CCM_C
#define MBEDTLS_CIPHER_C
#define MBEDTLS_CIPHER_MODE_CBC
#define MBEDTLS_CMAC_C
#define MBEDTLS_SSL_PROTO_DTLS
#define MBEDTLS_SSL_DTLS_ANTI_REPLAY
#define MBEDTLS_SSL_DTLS_HELLO_VERIFY
#define MBEDTLS_SSL_COOKIE_C
#define MBEDTLS_ECP_C
#define MBEDTLS_ECP_DP_SECP256R1_ENABLED
#define MBEDTLS_ECDH_C
#define MBEDTLS_ECDH_LEGACY_CONTEXT
#define MBEDTLS_ECDSA_C
#define MBEDTLS_ENTROPY_HARDWARE_ALT
#define MBEDTLS_ENTROPY_RAIL_PRESENT
#define MBEDTLS_MD_C
#define MBEDTLS_ECJPAKE_C
#define MBEDTLS_KEY_EXCHANGE_ECJPAKE_ENABLED
#define MBEDTLS_BIGNUM_C
#define MBEDTLS_PEM_PARSE_C
#define MBEDTLS_PEM_WRITE_C
#define MBEDTLS_ENTROPY_C
#define MBEDTLS_ENTROPY_FORCE_SHA256
#define MBEDTLS_ENTROPY_MAX_SOURCES 2
#define MBEDTLS_NO_PLATFORM_ENTROPY
#define MBEDTLS_CTR_DRBG_C
#define MBEDTLS_SHA256_C
#define MBEDTLS_SSL_TLS_C
#define MBEDTLS_SSL_CLI_C
#define MBEDTLS_SSL_PROTO_TLS1_2
#define MBEDTLS_SSL_KEEP_PEER_CERTIFICATE
#define MBEDTLS_SSL_SRV_C
#define MBEDTLS_X509_USE_C
#define MBEDTLS_X509_CREATE_C
#define MBEDTLS_X509_CRT_PARSE_C
#define MBEDTLS_X509_CRT_WRITE_C
#define MBEDTLS_X509_CRL_PARSE_C
#define MBEDTLS_X509_CSR_PARSE_C
#define MBEDTLS_X509_CSR_WRITE_C
#define MBEDTLS_OID_C
#define MBEDTLS_PK_C
#define MBEDTLS_PK_PARSE_C
#define MBEDTLS_PK_WRITE_C
#define MBEDTLS_PSA_CRYPTO_C
#define MBEDTLS_PSA_CRYPTO_CONFIG
#define MBEDTLS_PSA_CRYPTO_DRIVERS
#define MBEDTLS_PSA_CRYPTO_BUILTIN_KEYS
#define MBEDTLS_PSA_CRYPTO_STORAGE_C

#include "config-device-acceleration.h"

#if !defined(TEST_SUITE_MEMORY_BUFFER_ALLOC)
#if !defined(MBEDTLS_PLATFORM_FREE_MACRO) && !defined(MBEDTLS_PLATFORM_CALLOC_MACRO)
#if defined(CONFIG_MEDTLS_USE_AFR_MEMORY)
/* Amazon FreeRTOS requires custom memory allocator hooks */
#include <stddef.h>

extern void *pvCalloc(size_t xNumElements, size_t xSize);
extern void  vPortFree(void *pv);
#define MBEDTLS_PLATFORM_CALLOC_MACRO pvCalloc
#define MBEDTLS_PLATFORM_FREE_MACRO vPortFree
#else
/* No memory allocator override, supply the default for SL platforms */
#include "sl_malloc.h"

#define MBEDTLS_PLATFORM_FREE_MACRO sl_free
#define MBEDTLS_PLATFORM_CALLOC_MACRO sl_calloc
#endif
#endif /* No specific memory allocator override */
#endif /* Not under test */

#define MBEDTLS_PLATFORM_MEMORY
#define MBEDTLS_PLATFORM_C

#endif
