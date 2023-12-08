from conan import ConanFile
from conan.tools.cmake import CMake, cmake_layout
from conan.errors import ConanInvalidConfiguration


class Demo(ConanFile):
    settings = "os", "arch", "compiler", "build_type"
    generators = "CMakeDeps", "CMakeToolchain", "VirtualBuildEnv"

    @property
    def _compiler_version(self):
        SUPPORTED_COMPILER_VERSIONS = ["11.3", "12.2", "12.3"]

        if self.settings.compiler.version not in SUPPORTED_COMPILER_VERSIONS:
            raise ConanInvalidConfiguration(
                "The GCC compiler version must be one of these " +
                f"{SUPPORTED_COMPILER_VERSIONS}, provided version: " +
                f"'{self.settings.compiler.version}'")

        return str(self.settings.compiler.version)

    def validate(self):
        if self.settings.compiler != "gcc":
            raise ConanInvalidConfiguration(
                "This demo requires the compiler to be GCC, provided: " +
                f"'{self.settings.compiler}'")

        SUPPORTED_LIBC = ["nano", "nano_nosys"]
        if str(self.settings.compiler.libc) not in SUPPORTED_LIBC:
            raise ConanInvalidConfiguration(
                "libc must be defined and one of these " +
                f"{SUPPORTED_LIBC}, provided libc: " +
                f"'{self.settings.compiler.libc}'")

    def build_requirements(self):
        self.tool_requires("cmake/3.27.1")
        self.tool_requires(f"arm-gnu-toolchain/{self._compiler_version}")

    def requirements(self):
        pass

    def layout(self):
        libc = "build/" + str(self.settings.compiler.libc)
        cmake_layout(self, build_folder=libc)

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()
