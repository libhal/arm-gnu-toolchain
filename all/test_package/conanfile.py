from pathlib import Path
from conan import ConanFile
from conan.tools.cmake import CMake, cmake_layout
from conan.tools.build import cross_building


class TestPackageConan(ConanFile):
    settings = "os", "arch", "compiler", "build_type"
    generators = "CMakeDeps", "CMakeToolchain", "VirtualBuildEnv"

    def build_requirements(self):
        self.tool_requires("cmake/[^4.0.0]")
        self.tool_requires(self.tested_reference_str)

    def layout(self):
        cmake_layout(self)

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def test(self):
        # For cross-compilation toolchains, we just verify the binary was
        # created.
        # We cannot run ARM binaries on x86/ARM macOS/Linux/Windows hosts
        if cross_building(self):
            self.output.info(
                "Cross-compilation successful! Binary created for target architecture.")
            BINARY_PATH = Path(self.cpp.build.bindirs[0]) / "test_package"
            if not BINARY_PATH.exists():
                raise Exception(f"Expected binary not found at: {BINARY_PATH}")
            self.output.success(f"Test binary exists at: {BINARY_PATH}")
        else:
            APP = Path(self.cpp.build.bindirs[0]) / "test_package"
            self.run(APP, env="conanrun")
