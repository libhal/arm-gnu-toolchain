from pathlib import Path
from conan import ConanFile
from conan.tools.files import get, copy
from conan.errors import ConanInvalidConfiguration


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
    upload_policy = "skip"
    options = {
        "local_path": ["ANY"],
        "default_arch": [True, False],
        "lto": [True,  False],
        "fat_lto": [True,  False],
        "function_sections": [True,  False],
        "data_sections": [True,  False],
        "gc_sections": [True, False],
        "default_libc": [True, False]
    }

    default_options = {
        "local_path": "",
        "default_arch": True,
        "lto": True,
        "fat_lto": True,
        "function_sections": True,
        "data_sections": True,
        "gc_sections": True,
        "default_libc": True,
    }

    options_description = {
        "local_path": "Provide a path to your local ARM GNU Toolchain. If not set, the official toolchain is downloaded from the ARM website.",
        "default_arch": "Automatically inject architecture appropriate the -mcpu and -mfloat-abi arguments into compilation flags.",
        "lto": "Enable LTO support in binaries and intermediate files (.o and .a files)",
        "fat_lto": "Enable linkers without LTO support to still build with LTO enabled binaries. This adds both LTO information and compiled code into the object and archive files. This option is ignored if the `lto` option is False",
        "function_sections": "Enable -ffunction-sections which splits each function into their own subsection allowing link time garbage collection of the sections.",
        "data_sections": "Enable -fdata-sections which splits each statically defined block memory into their own subsection allowing link time garbage collection of the sections.",
        "gc_sections": "Enable garbage collection at link stage. Only useful if at least function_sections and data_sections is enabled.",
        "default_libc": "Link against `nosys` libc specification. This injects the `--specs=nosys.specs` argument to the linker during link. `nosys`  provides weak stubs for newlib libc APIs like exit(), kill(), sbrk() etc. This allows binaries to be linked without having to define all of the newlib libc definitions up front. It is UB to call any of these APIs without adding the necessary libc APIs. This is set to True in order to allow test_packages to link. It is not advised to depend on `libc` for C API definitions."
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

    def package(self):
        RESOURCE_DIR = Path(self.package_folder) / "res"
        copy(self, pattern="toolchain.cmake", src=self.source_folder,
             dst=RESOURCE_DIR, keep_path=True)

        # Use local path OR
        if self.options.local_path:
            self.package_local_path()
            return

        # Download the toolchain...
        OS = str(self._settings_build.os)
        VERSION = self.version
        ARCH = str(self._settings_build.arch)

        # For some reason ARM decided to make this version have a different
        # folder layout compared to others so we need a special case for this.
        should_strip_root = not (
            (VERSION == "14.2" or VERSION == "14.3" or VERSION == "14")
            and OS == "Windows" and ARCH == "x86_64")
        get(self,
            **self.conan_data["sources"][self.version][OS][ARCH],
            destination=self.package_folder, strip_root=should_strip_root)

    def package_local_path(self):
        LOCAL_PATH = str(self.options.local_path)
        self.output.info(f"self.options.local_path={LOCAL_PATH}")
        # Store the local path within a file named by the variable self.
        # LOCAL_PATH_TXT. When the package_info is invoked, this file will be
        # searched for and if it is found, will become the toolchain path.
        (Path(self.package_folder) / self.LOCAL_PATH_TXT).write_text(LOCAL_PATH)

    def setup_bin_dirs(self):
        LOCAL_PATH_FILE = Path(self.package_folder) / self.LOCAL_PATH_TXT
        if LOCAL_PATH_FILE.exists():
            self.output.info("Using binaries found within local_path")
            BIN_PATH = Path(LOCAL_PATH_FILE).read_text() / "bin"
        else:
            self.output.info("Using remote downloaded binaries")
            BIN_PATH = Path(self.package_folder) / "bin"

        self.cpp_info.bindirs = [BIN_PATH]

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

        # Blank out CMakeToolchain's default optimization flags
        # We manage all flags ourselves via tools.build:cxxflags
        self.conf_info.define("tools.cmake.cmaketoolchain:extra_variables", {
            # Blank out CMake's default optimization flags
            "CMAKE_CXX_FLAGS_DEBUG": "",
            "CMAKE_CXX_FLAGS_RELEASE": "",
            "CMAKE_CXX_FLAGS_MINSIZEREL": "",
            "CMAKE_CXX_FLAGS_RELWITHDEBINFO": "",
            "CMAKE_C_FLAGS_DEBUG": "",
            "CMAKE_C_FLAGS_RELEASE": "",
            "CMAKE_C_FLAGS_MINSIZEREL": "",
            "CMAKE_C_FLAGS_RELWITHDEBINFO": "",

            # Cross-compilation workarounds
            "CMAKE_CXX_COMPILER_WORKS": "TRUE",
            "CMAKE_C_COMPILER_WORKS": "TRUE",
            "CMAKE_TRY_COMPILE_TARGET_TYPE": "STATIC_LIBRARY",

            # Binutils
            "CMAKE_AR": "arm-none-eabi-ar",
            "CMAKE_RANLIB": "arm-none-eabi-ranlib",
        })

        TOOLCHAIN_PATH = str(Path(self.package_folder) / "res/toolchain.cmake")
        self.conf_info.append(
            "tools.cmake.cmaketoolchain:user_toolchain", TOOLCHAIN_PATH)

        self.setup_bin_dirs()
        self.inject_c_cxx_and_link_flags()

    def inject_c_cxx_and_link_flags(self):
        c_flags = []
        cxx_flags = []
        exelinkflags = []

        if self.settings_target:
            # Set optimization level based on build type
            BUILD_TYPE = str(self.settings_target.build_type)
            if BUILD_TYPE == "Debug":
                # Use -Og for debuggable but LTO-compatible code
                c_flags.append("-Og")
                cxx_flags.append("-Og")
                # Note about Og and O0. If you use LTO with O0, LTO seems to
                # lose track of the symbols and gives an error stating that some
                # symbols cannot be found like std::pmr::memory_resource or
                # atomic operations. There seems to be some sort of issue of
                # disabling optimizations but also enabling link time
                # optimizations. To get over this, we've chosen to use `-Og` as
                # your Debug build. This also provides the added benefit of
                # apply reasonable optimizations, reducing binary size and
                # improving performance without reducing debuggability.
            elif BUILD_TYPE == "MinSizeRel":
                # -Os prioritizes size optimizations
                c_flags.append("-Os")
                cxx_flags.append("-Os")
            elif BUILD_TYPE in ["Release", "RelWithDebInfo"]:
                # Use -O3 for maximum performance at the expense of space
                c_flags.append("-O3")
                cxx_flags.append("-O3")

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

        if self.options.default_libc:
            exelinkflags.append("--specs=nosys.specs")

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
        # Clear everything - this is a recipe-only package
        # Users build locally by downloading binaries for their platform
        self.info.clear()
