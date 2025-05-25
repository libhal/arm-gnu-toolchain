cmake_minimum_required(VERSION 3.15)
project(demo LANGUAGES CXX)
add_executable(demo main.cpp)

# Needed to link in low level C APIs
target_link_options(demo PRIVATE --specs=nano.specs --specs=nosys.specs)
