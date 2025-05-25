cmake_minimum_required(VERSION 3.15)

set(CMAKE_TOOLCHAIN_FILE ../toolchain.cmake)

project(test_package LANGUAGES CXX)

add_executable(test_package main.cpp)

# These are added here because conan will not propagate this information to
# test packages due to the build target being the host OS.
target_compile_options(test_package PRIVATE -mcpu=cortex-m0)
target_link_options(test_package PRIVATE -mcpu=cortex-m0
  --specs=nano.specs --specs=nosys.specs)
