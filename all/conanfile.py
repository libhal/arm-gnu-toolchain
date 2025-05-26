from pathlib import Path
from conan import ConanFile
from conan.tools.files import get, copy, download
from conan.errors import ConanInvalidConfiguration
import os


required_conan_version = ">=2.0.0"


class ArmGnuToolchain(ConanFile):
    name = "arm-gnu-toolchain"
    license = ("GPL-3.0-only", "GPL-2.0-only", "BSD-3-Clause",
               "BSD-2-Clause-FreeBSD", "AGPL-3.0-only", "BSD-2-Clause")
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://developer.arm.com/downloads/-/arm-gnu-toolchain-downloads"
    description = ("Conan installer for the GNU Arm Embedded Toolchain")
    topics = ("gcc", "compiler", "embedded", "arm", "cortex", "cortex-m",
              "cortex-m0", "cortex-m0+", "cortex-m1", "cortex-m3", "cortex-m4",
              "cortex-m4f", "cortex-m7", "cortex-m23", "cortex-m55",
              "cortex-m35p", "cortex-m33")
    settings = "os", "arch", "compiler", "build_type"
    exports_sources = "toolchain.cmake"
    package_type = "application"
    build_policy = "missing"
    short_paths = True
    options = {
        "local_path": ["ANY"],
        "default_arch": [True, False],
        "lto": [True,  False],
        "fat_lto": [True,  False],
        "function_sections": [True,  False],
        "data_sections": [True,  False],
        "gc_sections": [True, False],
    }

    default_options = {
        "local_path": "",
        "default_arch": True,
        "lto": True,
        "fat_lto": True,
        "function_sections": True,
        "data_sections": True,
        "gc_sections": True,
    }

    options_description = {
        "local_path": "Provide a path to your local ARM GNU Toolchain. If not set, the official toolchain is downloaded from the ARM website.",
        "default_arch": "Automatically inject architecture appropriate the -mcpu and -mfloat-abi arguments into compilation flags.",
        "lto": "Enable LTO support in binaries and intermediate files (.o and .a files)",
        "fat_lto": "Enable linkers without LTO support to still build with LTO enabled binaries. This adds both LTO information and compiled code into the object and archive files.",
        "function_sections": "Enable -ffunction-sections which splits each function into their own subsection allowing link time garbage collection of the sections.",
        "data_sections": "Enable -fdata-sections which splits each statically defined block memory into their own subsection allowing link time garbage collection of the sections.",
        "gc_sections": "Enable garbage collection at link stage. Only useful if at least function_sections and data_sections is enabled."
    }

    LOCAL_PATH_TXT = "local_path.txt"

    @property
    def _settings_build(self):
        return getattr(self, "settings_build", self.settings)

    def validate(self):
        supported_build_operating_systems = ["Linux", "Macos", "Windows"]
        if not self._settings_build.os in supported_build_operating_systems:
            raise ConanInvalidConfiguration(
                f"The build os '{self._settings_build.os}' is not supported. "
                "Pre-compiled binaries are only available for "
                f"{supported_build_operating_systems}."
            )

        supported_build_architectures = {
            "Linux": ["armv8", "x86_64"],
            "Macos": ["armv8", "x86_64"],
            "Windows": ["x86_64"],
        }

        if (
            not self._settings_build.arch
            in supported_build_architectures[str(self._settings_build.os)]
        ):
            build_os = str(self._settings_build.os)
            raise ConanInvalidConfiguration(
                f"The build architecture '{self._settings_build.arch}' "
                f"is not supported for {self._settings_build.os}. "
                "Pre-compiled binaries are only available for "
                f"{supported_build_architectures[build_os]}."
            )

    def build(self):
        if self.options.local_path:
            return  # Nothing to do here
        # Otherwise, download the toolchain

        VERSION_MAP = {
            # License URL found from the "EULA" button on the
            # https://developer.arm.com/downloads/-/arm-gnu-toolchain-downloads
            # web page.
            "11.3": "https://developer.arm.com/GetEula?Id=ff19df33-da82-491a-ab50-c605d4589a26",
            "12.2": "https://developer.arm.com/GetEula?Id=2821586b-44d0-4e75-a06d-4279cd97eaae",
            "12.3": "https://developer.arm.com/GetEula?Id=aa3d692d-bc99-4c8c-bce2-588181ddde13",
            "13.2": "https://developer.arm.com/GetEula?Id=37988a7c-c40e-4b78-9fd1-62c20b507aa8",
            "13.3": "https://developer.arm.com/GetEula?Id=d023c29f-8e81-49b0-979f-a5610ea2ccbb",
            "14.2": "https://developer.arm.com/GetEula?Id=3aa52a53-d1cb-414b-b540-eaf29fdef0ca",
        }

        if self.version in VERSION_MAP:
            download(self, VERSION_MAP[self.version], "LICENSE", verify=False)

        OS = str(self._settings_build.os)
        VERSION = self.version
        ARCH = str(self._settings_build.arch)

        # For some reason ARM decided to make this version have a different
        # folder layout compared to others so we need a special case for this.
        should_strip_root = not (VERSION == "14.2" and OS ==
                                 "Windows" and ARCH == "x86_64")
        get(self,
            **self.conan_data["sources"][self.version][OS][ARCH],
            destination=self.build_folder, strip_root=should_strip_root)

    def package_local_path(self):
        LOCAL_PATH = str(self.options.local_path)
        self.output.info(f"self.options.local_path={LOCAL_PATH}")
        # Store the local path within a file named by the variable self.
        # LOCAL_PATH_TXT. When the package_info is invoked, this file will be
        # searched for and if it is found, will become the toolchain path.
        Path(os.path.join(self.package_folder, self.LOCAL_PATH_TXT)
             ).write_text(LOCAL_PATH)

    def package_remote_path(self):
        LICENSE_DIR = os.path.join(self.package_folder, "licenses")
        copy(self, pattern="LICENSE*", src=self.build_folder,
             dst=LICENSE_DIR, keep_path=True)

        DESTINATION = os.path.join(self.package_folder, "bin")
        DIRECTORIES_TO_COPY = ["arm-none-eabi", "bin",
                               "include", "lib", "libexec", "share"]
        for directory in DIRECTORIES_TO_COPY:
            copy(self, pattern=f"{directory}/*", src=self.build_folder,
                 dst=DESTINATION, keep_path=True)

    def package(self):
        RESOURCE_DIR = os.path.join(self.package_folder, "res/")
        copy(self, pattern="toolchain.cmake", src=self.build_folder,
             dst=RESOURCE_DIR, keep_path=True)
        if self.options.local_path:
            self.package_local_path()
        else:
            self.package_remote_path()

    def setup_local_package_info(self):
        self.output.info("Using binaries found within local_path.txt")
        LOCAL_PATH = Path(os.path.join(
            self.package_folder, self.LOCAL_PATH_TXT)).read_text()
        bin_folder = os.path.join(LOCAL_PATH, "bin/")
        self.cpp_info.bindirs = [bin_folder]

    def setup_remote_package_info(self):
        self.output.info("Using remote downloaded binaries")
        bin_folder = os.path.join(os.path.join(
            self.package_folder, "bin"), "bin")
        self.cpp_info.bindirs = [bin_folder]

    def setup_bin_dirs(self):
        LOCAL_PATH_FILE = os.path.join(
            self.package_folder, self.LOCAL_PATH_TXT)
        if os.path.exists(LOCAL_PATH_FILE):
            self.output.info("Using binaries found within local_path")
            bin_path = Path(LOCAL_PATH_FILE).read_text()
        else:
            self.output.info("Using remote downloaded binaries")
            bin_path = os.path.join(self.package_folder, "bin")

        # This should contain the command `arm-none-eabi-g++` and others
        bin_folder = os.path.join(bin_path, "bin")

        # This cpp_info is transmitted to the consumer's PATH
        self.cpp_info.bindirs = [bin_folder]

        self.output.info(f"self.cpp_info.bindirs = {self.cpp_info.bindirs}")

    def package_info(self):
        self.cpp_info.includedirs = []
        self.conf_info.define(
            "tools.cmake.cmaketoolchain:system_name", "Generic")
        self.conf_info.define(
            "tools.cmake.cmaketoolchain:system_processor", "ARM")
        self.conf_info.define("tools.build.cross_building:can_run", False)
        self.conf_info.define("tools.build:compiler_executables", {
            "c": "arm-none-eabi-gcc",
            "cpp": "arm-none-eabi-g++",
            "asm": "arm-none-eabi-gcc",
        })
        f = os.path.join(self.package_folder, "res/toolchain.cmake")
        self.conf_info.append("tools.cmake.cmaketoolchain:user_toolchain", f)

        self.setup_bin_dirs()
        self.inject_c_cxx_and_link_flags()

    def inject_c_cxx_and_link_flags(self):
        c_flags = []
        cxx_flags = []
        exelinkflags = []

        if self.options.lto:
            c_flags.append("-flto")
            cxx_flags.append("-flto")
            exelinkflags.append("-flto")

        if self.options.fat_lto:
            c_flags.append("-ffat-lto-objects")
            cxx_flags.append("-ffat-lto-objects")

        if self.options.function_sections:
            c_flags.append("-ffunction-sections")
            cxx_flags.append("-ffunction-sections")

        if self.options.data_sections:
            c_flags.append("-fdata-sections")
            cxx_flags.append("-fdata-sections")

        if self.options.gc_sections:
            exelinkflags.append("-Wl,--gc-sections")

        ARCH_MAP = {
            "cortex-m0": ["-mcpu=cortex-m0", "-mfloat-abi=soft"],
            "cortex-m0plus": ["-mcpu=cortex-m0plus", "-mfloat-abi=soft"],
            "cortex-m1": ["-mcpu=cortex-m1", "-mfloat-abi=soft"],
            "cortex-m3": ["-mcpu=cortex-m3", "-mfloat-abi=soft"],
            "cortex-m4": ["-mcpu=cortex-m4", "-mfloat-abi=soft"],
            "cortex-m4f": ["-mcpu=cortex-m4", "-mfloat-abi=hard"],
            "cortex-m7": ["-mcpu=cortex-m7", "-mfloat-abi=soft"],
            "cortex-m7f": [
                "-mcpu=cortex-m7", "-mfloat-abi=hard", "-mfpu=fpv5-sp-d16"],
            "cortex-m7d": [
                "-mcpu=cortex-m7", "-mfloat-abi=hard", "-mfpu=fpv5-d16"],
            "cortex-m23": ["-mcpu=cortex-m23", "-mfloat-abi=soft"],
            "cortex-m33": ["-mcpu=cortex-m33", "-mfloat-abi=soft"],
            "cortex-m33f": ["-mcpu=cortex-m33", "-mfloat-abi=hard"],
            "cortex-m33p": ["-mcpu=cortex-m33p", "-mfloat-abi=soft"],
            "cortex-m35pf": ["-mcpu=cortex-m35p", "-mfloat-abi=hard"],
            "cortex-m55": ["-mcpu=cortex-m55", "-mfloat-abi=soft"],
            # TODO: Add "cortex-m55" half floating point
            # TODO: Add "cortex-m55" single floating point
            # TODO: Add "cortex-m55" double floating point
            "cortex-m85": ["-mcpu=cortex-m85", "-mfloat-abi=soft"],
            # TODO: Add "cortex-m85" half floating point
            # TODO: Add "cortex-m85" single floating point
            # TODO: Add "cortex-m85" double floating point
        }

        if (self.options.default_arch and self.settings_target and
                self.settings_target.get_safe('arch') in ARCH_MAP):
            ARCH_FLAGS = ARCH_MAP[self.settings_target.get_safe('arch')]
            c_flags.extend(ARCH_FLAGS)
            cxx_flags.extend(ARCH_FLAGS)
            exelinkflags.extend(ARCH_FLAGS)

        self.output.info(f'c_flags: {c_flags}')
        self.output.info(f'cxx_flags: {cxx_flags}')
        self.output.info(f'exelinkflags: {exelinkflags}')

        self.conf_info.append("tools.build:cflags", c_flags)
        self.conf_info.append("tools.build:cxxflags", cxx_flags)
        self.conf_info.append("tools.build:exelinkflags", exelinkflags)

    def package_id(self):
        del self.info.options.local_path
        del self.info.options.default_arch
        del self.info.options.lto
        del self.info.options.fat_lto
        del self.info.options.function_sections
        del self.info.options.data_sections
        del self.info.options.gc_sections
