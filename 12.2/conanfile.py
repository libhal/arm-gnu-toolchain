from conan.errors import ConanInvalidConfiguration
from conan import ConanFile
from conan.tools.files import get, copy
import os


required_conan_version = ">=1.50.0"


class GnuArmEmbeddedToolchain(ConanFile):
    name = "gnu-arm-embedded-toolchain"
    # All changes to the version number will be in patch. The first two numbers
    # Represent the GCC version. The patch number represents changes to the
    # recipe or toolchain.cmake file
    version = "12.2.0"
    license = "GPL-3.0-only"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://developer.arm.com/downloads/-/arm-gnu-toolchain-downloads"
    description = ("Conan installer for the GNU Arm Embedded Toolchain")
    topics = ("ARM", "cortex", "cortex-m", "cortex-m0", "cortex-m0+",
              "cortex-m1", "cortex-m3", "cortex-m4", "cortex-m4f", "cortex-m7",
              "cortex-m23", "cortex-m55", "cortex-m35p", "cortex-m33")
    settings = "os", "arch"
    build_policy = "missing"

    def validate(self):
        pass

    @property
    def arm_toolchain_archive(self):
        if self.settings.os == "Windows":
            return "gnu-arm-embedded-toolchain.zip"
        return "gnu-arm-embedded-toolchain.tar.xz"

    @property
    def download_link(self):
        if self.settings.os == "Windows":
            return "https://github.com/libhal/gnu-arm-embedded-toolchain/releases/download/v12.2/arm-gnu-toolchain-12.2.rel1-mingw-w64-i686-arm-none-eabi.zip"
        if str(self.settings.arch).startswith("arm") and self.settings.os == "Linux":
            return "https://github.com/libhal/gnu-arm-embedded-toolchain/releases/download/v12.2/arm-gnu-toolchain-12.2.rel1-aarch64-arm-none-eabi.tar.xz"
        if self.settings.arch == "x86_64" and self.settings.os == "Linux":
            return "https://github.com/libhal/gnu-arm-embedded-toolchain/releases/download/v12.2/arm-gnu-toolchain-12.2.rel1-x86_64-arm-none-eabi.tar.xz"
        if self.settings.arch == "x86_64" and self.settings.os == "Macos":
            return "https://github.com/libhal/gnu-arm-embedded-toolchain/releases/download/v12.2/arm-gnu-toolchain-12.2.rel1-darwin-x86_64-arm-none-eabi.tar.xz"
        if str(self.settings.arch).startswith("arm") and self.settings.os == "Macos":
            return "https://github.com/libhal/gnu-arm-embedded-toolchain/releases/download/v12.2/arm-gnu-toolchain-12.2.rel1-darwin-arm64-arm-none-eabi.tar.xz"
        else:
            raise ConanInvalidConfiguration(
                f"The OS {self.settings.os} and architecture {self.settings.arch} is not supported")

    def build(self):
        self.output.info(
            f"Downloading GNU Arm Embedded Toolchain: {self.download_link}")
        get(self, self.download_link, strip_root=True)

    def package(self):
        copy(self, pattern="*", src=self.build_folder,
             dst=self.package_folder, keep_path=True)

    def package_info(self):
        # Add bin directory to PATH
        bin_folder = os.path.join(self.package_folder, "bin")
        self.env_info.PATH.append(bin_folder)
        self.cpp_info.bindirs = [bin_folder]
