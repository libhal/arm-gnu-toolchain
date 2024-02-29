# Append current directory to CMAKE_MODULE_PATH for making device specific
# cmake modules visible
list(APPEND CMAKE_MODULE_PATH ${CMAKE_CURRENT_LIST_DIR})

# Skip Working compiler test which tends to fail in CMake due to it using build
# target architecture flags and not host architecture flags.
set(CMAKE_CXX_COMPILER_WORKS TRUE)
set(CMAKE_C_COMPILER_WORKS TRUE)

# Need to force system to Generic & ARM as leaving this to Conan will result in
# pollution from host profile settings
set(CMAKE_SYSTEM_NAME Generic)
set(CMAKE_SYSTEM_PROCESSOR arm)

# Target definition
set(TOOLCHAIN arm-none-eabi)

# Perform compiler test with static library
set(CMAKE_TRY_COMPILE_TARGET_TYPE STATIC_LIBRARY)

# Set toolchain compilers
set(CMAKE_C_COMPILER ${TOOLCHAIN}-gcc${CMAKE_EXECUTABLE_SUFFIX})
set(CMAKE_CXX_COMPILER ${TOOLCHAIN}-g++${CMAKE_EXECUTABLE_SUFFIX})
set(CMAKE_ASM_COMPILER ${TOOLCHAIN}-gcc${CMAKE_EXECUTABLE_SUFFIX})
set(CMAKE_AR ${TOOLCHAIN}-ar${CMAKE_EXECUTABLE_SUFFIX})
set(CMAKE_SIZE_UTIL ${TOOLCHAIN}-size${CMAKE_EXECUTABLE_SUFFIX})
set(CMAKE_OBJDUMP ${TOOLCHAIN}-objdump${CMAKE_EXECUTABLE_SUFFIX})
set(CMAKE_OBJCOPY ${TOOLCHAIN}-objcopy${CMAKE_EXECUTABLE_SUFFIX})
set(CMAKE_FIND_ROOT_PATH ${CMAKE_PREFIX_PATH} ${CMAKE_BINARY_DIR})

set(CMAKE_FIND_ROOT_PATH_MODE_PROGRAM NEVER)
set(CMAKE_FIND_ROOT_PATH_MODE_LIBRARY ONLY)
set(CMAKE_FIND_ROOT_PATH_MODE_INCLUDE ONLY)
set(CMAKE_FIND_ROOT_PATH_MODE_PACKAGE ONLY)

if(DEFINED CONAN_LIBC AND CONAN_LIBC STREQUAL "custom")
  message(STATUS "Custom libc selected. No link flags injected!")
else()
  message(STATUS "Default libc used!")

  set(NANO_SPECS_FLAG "--specs=nano.specs")
  if(NOT CMAKE_EXE_LINKER_FLAGS MATCHES ${NANO_SPECS_FLAG})
    message(STATUS "Injecting linker flag ${NANO_SPECS_FLAG}")
    string(APPEND CMAKE_EXE_LINKER_FLAGS " ${NANO_SPECS_FLAG}")
  endif()

  set(NOSYS_SPECS_FLAG "--specs=nosys.specs")
  if(NOT CMAKE_EXE_LINKER_FLAGS MATCHES ${NOSYS_SPECS_FLAG})
    message(STATUS "Injecting linker flag ${NOSYS_SPECS_FLAG}")
    string(APPEND CMAKE_EXE_LINKER_FLAGS " ${NOSYS_SPECS_FLAG}")
  endif()
endif()
