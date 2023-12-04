from conan import ConanFile
from conan.tools.cmake import CMake, cmake_layout


class Demo(ConanFile):
    settings = "os", "arch", "compiler", "build_type"
    generators = "CMakeDeps", "CMakeToolchain", "VirtualBuildEnv"

    @property
    def _uses_picolibc(self):
        return self.settings.compiler.get_safe("libc") == "picolibc"

    def build_requirements(self):
        self.tool_requires("cmake/3.27.1")
        self.tool_requires("arm-gnu-toolchain/12.2.1")

    def requirements(self):
        pass

    def layout(self):
        libc = "build/" + str(self.settings.compiler.libc)
        cmake_layout(self, build_folder=libc)

    def build(self):
        cmake = CMake(self)
        cmake.configure(variables={"USES_PICOLIBC": self._uses_picolibc})
        cmake.build()
