# VM Specifications

## System Overview

| Property | Value |
|----------|-------|
| Hostname | `runsc` |
| User | `root` |
| OS | Ubuntu 24.04.3 LTS (Noble Numbat) |
| Kernel | Linux 4.4.0 x86_64 |
| Hypervisor | KVM |
| Virtualization | Full (VT-x) |

## CPU

| Property | Value |
|----------|-------|
| Architecture | x86_64 |
| Vendor | GenuineIntel |
| CPU Family | 6, Model 207 |
| Cores | 16 (1 socket, 16 cores/socket, 1 thread/core) |
| Clock Speed | 2100 MHz |
| Cache | 8192 KB |
| Notable Extensions | AVX-512, AMX, SHA-NI, AES |

## Memory

| Property | Value |
|----------|-------|
| Total RAM | 21 GiB (~22 GB) |
| Swap | None |

## Storage

| Filesystem | Size | Used | Available | Mount |
|------------|------|------|-----------|-------|
| Root (`/`) | 30G | 13M | 30G | none |
| `/dev` | 315G | 0 | 315G | none |
| `/dev/shm` | 315G | 0 | 315G | none |

## Installed Development Tools

| Tool | Version |
|------|---------|
| Python | 3.11.14 |
| Node.js | 22.22.0 |
| Git | 2.43.0 |
| GCC | 13.3.0 |
| Go | 1.24.7 |
| Rust | 1.93.1 |
| Java (OpenJDK) | 21.0.10 |
| Docker | 29.2.1 |
