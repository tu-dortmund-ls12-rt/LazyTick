# The following lines of boilerplate have to be in your project's
# CMakeLists in this exact order for cmake to work correctly
cmake_minimum_required(VERSION 3.16)

set(COMPONENTS cxx newlib freertos esp_hw_support heap log soc hal esp_rom esp_common esp_system esp_psram spi_flash driver main)
# set(EXCLUDE_COMPONENTS efuse lwip vfs esp_wifi esp_event esp_netif esp_eth esp_phy)
include(./esp-idf/tools/cmake/project.cmake)
project(lazytick)
idf_build_set_property(COMPILE_OPTIONS "-fdiagnostics-color=always" APPEND)
