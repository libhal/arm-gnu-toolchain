from conan import ConanFile
from conan.errors import ConanInvalidConfiguration

required_conan_version = ">=2.0.6"


class Picolibc(ConanFile):
    name = "picolibc"
    version = "0.0.1"
    settings = "os", "arch", "compiler", "build_type"
    package_type = "static-library"
    short_paths = True
    options = {
        "crt0": [
            "semihost",
            "hosted",
            "minimal",
        ]
    }
    default_options = {
        "crt0": "semihost",
    }

    @property
    def _link_flags(self):
        return ["--specs=/path/to/picolibc.specs",
                f"--oslib={str(self.options.crt0)}"]

    def package_id(self):
        self.info.clear()

    def validate(self):
        return

    def source(self):
        pass

    def build(self):
        pass

    def package(self):
        pass

    def package_info(self):
        self.cpp_info.set_property("cmake_target_name", "picolibc")
        self.cpp_info.libs = []
        self.cpp_info.includedirs = []
        self.cpp_info.bindirs = []
        self.cpp_info.frameworkdirs = []
        self.cpp_info.libdirs = []
        self.cpp_info.resdirs = []
        self.cpp_info.exelinkflags = self._link_flags

        self.output.info(f"link flags: {self._link_flags}")
        self.output.info(f"crt0: {str(self.options.crt0)}")
