cmake_minimum_required(VERSION 3.15)

set(CMAKE_TOOLCHAIN_FILE ../toolchain.cmake)

project(test_package LANGUAGES CXX)

add_executable(${PROJECT_NAME} main.cpp)
target_compile_options(${PROJECT_NAME} PRIVATE
  -mcpu=cortex-m0
  --specs=nosys.specs)

target_link_options(${PROJECT_NAME} PRIVATE
  -mcpu=cortex-m0
  --specs=nosys.specs)
