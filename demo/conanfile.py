from conan import ConanFile
from conan.tools.cmake import CMake, cmake_layout
from conan.errors import ConanInvalidConfiguration


class Demo(ConanFile):
    settings = "os", "arch", "compiler", "build_type"
    generators = "CMakeDeps", "CMakeToolchain", "VirtualBuildEnv"

    def validate(self):
        if self.settings.compiler != "gcc":
            raise ConanInvalidConfiguration(
                "This demo requires the compiler to be GCC, provided: " +
                f"'{self.settings.compiler}'")

    def build_requirements(self):
        self.tool_requires("cmake/3.27.1")

    def requirements(self):
        pass

    def layout(self):
        cmake_layout(self)

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()
