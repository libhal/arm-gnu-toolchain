from conan import ConanFile
from conan.tools.cmake import CMake, cmake_layout


class Demo(ConanFile):
    settings = "os", "arch", "compiler", "build_type"
    generators = "CMakeDeps", "CMakeToolchain", "VirtualBuildEnv"
    options = {"stdlibc": ["ANY"]}
    default_options = {"stdlibc": "unspecified"}

    def build_requirements(self):
        self.tool_requires("cmake/3.27.1")
        _PASS_STDLIBC_VIA_HOST_OPTIONS = True
        if _PASS_STDLIBC_VIA_HOST_OPTIONS:
            self.tool_requires("arm-gnu-toolchain/12.2.1", options={
                "stdlibc": str(self.options.stdlibc)
            })
        else:
            self.tool_requires("arm-gnu-toolchain/12.2.1")

    def requirements(self):
        self.requires("picolibc/0.0.1")

    def layout(self):
        cmake_layout(self)

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()
