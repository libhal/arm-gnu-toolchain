# ARM GNU Toolchain Repo

Here you can find conan packages for the ARM GNU Toolchain packages used by
libhal project.

## 🏗️ Build Demo

```bash
conan create all --version 12.2.1
conan create demo/picolibc_test_pkg --version 12.2.1
conan build demo -pr demo/profile
```

The demo package will not succeed, but what is more important is that the
arm compiler and picolibc flags are present in the commands. They can be exposed
by adding `VERBOSE=1` in front of the command.
