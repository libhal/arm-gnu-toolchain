# gnu-arm-embedded-toolchain

To use this with conan add this line to your `conanfile.txt`:

```
[tool_requires]
gnu-arm-embedded-toolchain/11.3.0
```

The `libhal-trunk` server doesn't cache the binaries because they are cached
by github so when you run `conan install`, you will need to add
`--build=missing`.

## Using with CMake & Conan

The following `conanfile.txt` will enable cross compiling with conan and cmake:

```bash
[requires]
# target libraries here

[tool_requires]
gnu-arm-embedded-toolchain/11.3.0
cmake-arm-embedded/0.1.1

[generators]
CMakeDeps
CMakeToolchain
```

Then when running `cmake` make sure to set the `conan_toolchain.cmake` as the
`CMAKE_TOOLCHAIN_FILE`.

```bash
cmake .. -D CMAKE_TOOLCHAIN_FILE=conan_toolchain.cmake
```
