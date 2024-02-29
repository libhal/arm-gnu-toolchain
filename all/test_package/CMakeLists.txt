cmake_minimum_required(VERSION 3.15)

set(CMAKE_TOOLCHAIN_FILE ../toolchain.cmake)

project(test_package LANGUAGES CXX)

add_executable(test_package main.cpp)
target_compile_options(test_package PRIVATE -mcpu=cortex-m0)
target_link_options(test_package PRIVATE -mcpu=cortex-m0)
