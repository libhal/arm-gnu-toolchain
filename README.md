# ARM GNU Toolchain Repo

A conan tool package for the ARM GNU Toolchain (`arm-none-eabi-gcc`). By adding
this tool package to your conan build profile, your project will be cross compiled using this toolchain.

Supported version:

- GCC 11.3
- GCC 12.2
- GCC 12.3
- GCC 13.2
- GCC 13.3
- GCC 14.2

All binaries are downloaded from the official
[ARM GNU Toolchain Download Page](https://developer.arm.com/downloads/-/arm-gnu-toolchain-downloads).

## 🚀 Quick Start

For this tool package to work correctly, the toolchain **MUST** be a dependency
within your build profile like so:

```jinja2
[settings]
compiler=gcc
compiler.cppstd=23
compiler.libcxx=libstdc++11
compiler.version=11.3

[tool_requires]
arm-gnu-toolchain/11.3
```

By adding it to your profile, every dependency of your application will use this
toolchain for its compilation. The tool package should NOT be directly added to
an application's `conanfile.py` as this will not propagate correctly and will
likely result in build failures.

## 🧾 Using the pre-made profiles

This repo provides are pre-made profiles within the `conan/profiles/`
directory. The profiles can be installed into your local conan cache directory
via this command:

```bash
conan config install -sf conan/profiles/v1 -tf profiles https://github.com/libhal/arm-gnu-toolchain.git
```

To perform this with a locally cloned repo run this command at the root of the
repo:

```bash
conan config install -sf conan/profiles/v1 -tf profiles .
```

Profiles are versioned in directories `v1/`, `v2/`, `v3/`, etc. Currently there
are no sub versions. The version increment is not well defined as of yet, but
should be incremented if the behavior of the profiles changes significantly
enough to break current applications.

The pre-made profiles come with decision decision which may not align with your
application.

### **Design Decisions:** LTO & FAT LTO

The `v1` profiles add the following to enable LTO and FAT LTO.

```plaintext
[conf]
tools.build:cflags=["-flto", "-ffat-lto-objects"]
tools.build:cxxflags=["-flto", "-ffat-lto-objects"]
tools.build:exelinkflags=["-flto"]
tools.build:sharedlinkflags=["-flto"]
```

LTO stands for Link Time Optimization. Enabling it changes the representation
of the intermediate files (object files and archive files) to a form that that
can better be optimized by the linker. This tends to improve performance and
reduce binary sizes. Intermediate files generated with LTO only work with
linkers that support LTO and have LTO enabled. FAT LTO provides both the LTO
and original compiled representation which enabling linkers with and without
linker support to link correctly.

The cost is that the intermediate files get larger and build times may get
longer. It is likely that targets using this compiler will have low resources
and could benefit from the added optimization, thus all profiles have LTO
enabled.

### **Design Decisions:** `libstdc++11`

The `v1` profiles all use `libstdc++11` as this is the latest GCC C++ ABI.
There is not much value in the older ABI and thus we use the latest. There is
currently no plan for what the profiles will become if a new C++ ABI is
introduced.

## 📦 Building & Installing the Tool Package

When you create the package it will download the compiler from the official website and store it within your local conan package cache.

```bash
conan create . --version <insert version>
```

For example, to create/install GCC 12.3

```bash
conan create . --version 12.3
```

## Using Non-Official ARM Toolchain Builds

Are you building the toolchain locally? Are you using prebuilt binaries from
some other source? If so, use the `local_path` option to set the path to
the local toolchain root. This will replace the download step completely and
will assume that all of the necessary files are within the `local_path`
directory.

To create a GCC version 14.2 pointed to `/path/to/arm-gnu-toolchain-root/`

```bash
conan create . --version 14.2 -o "*:local_path=/path/to/arm-gnu-toolchain-root/
```

Make sure the toolchain and the version of the package match otherwise, the
compiler package may not work correctly.

## ✨ Adding New Versions of GCC

If ARM produces a new GCC version on their
["Arm GNU Toolchain Downloads"](https://developer.arm.com/downloads/-/arm-gnu-toolchain-downloads)
page and you'd like for the conan package to also support that version of GCC,
please follow these instructions and replace `XY.Z` with the correct GCC
version.

1. Add version to the `/config.yml` file. Should look like
   this:

  ```yaml
  versions:
    "11.3":
      folder: "all"
    "12.2":
      folder: "all"
    "12.3":
      folder: "all"
    "XY.Z":
      folder: "all"
  ```

2. Add file `XY.Z.yml` to `/.github/workflows/` with the
   following contents:

  ```yaml
  name: 🚀 12.3 Deploy

  on:
    workflow_dispatch:
    pull_request:
    push:
      branches:
        - main

  jobs:
    deploy:
      uses: ./.github/workflows/deploy.yml
      with:
        version: "XY.Z"
      secrets: inherit
  ```

3. Add profile `arm-gcc-XY.Z` to directory `/conan/profiles/v1` with the
   following contents:

  ```yaml
  [settings]
  compiler=gcc
  compiler.cppstd=23
  compiler.libcxx=libstdc++11
  compiler.version=XY.Z

  [tool_requires]
  arm-gnu-toolchain/XY.Z
  ```

4. Add License for ARM GNU Toolchain version `XY.Z`. This can be done by
   right-clicking on the `EULA` button and clicking on the "Copy Link Address"
   option as shown in this picture:

![Red box bounding the are where the ARM EULA license file button is located](./assets/eula_button.webp "ARM EULA License Button")

5. Add the download URL & SHA256 hash for each of the following fields in the
   `all/conandata.yml` file. We only want cross compilers for the
   `AArch32 bare-metal target (arm-none-eabi)`. See section [finding download urls](#finding-download-urls) for more information about how to acquire this information.

  ```yaml
  sources:
    "XY.Z":
      "Linux":
        "x86_64":
          url: ""
          sha256: ""
        "armv8":
          url: ""
          sha256: ""
      "Macos":
        "x86_64":
          url: ""
          sha256: ""
        "armv8":
          url: ""
          sha256: ""
      "Windows":
        "x86_64":
          url: ""
          sha256: ""
  ```

6. DONE! Congratz you did it. Make a PR with the title
   `:sparkles: Add support for GCC XY.Z`.

## Finding Download URLs

The URLs on the download website look like this:

```plaintext
https://developer.arm.com/-/media/Files/downloads/gnu/13.2.rel1/binrel/arm-gnu-toolchain-13.2.rel1-aarch64-arm-none-eabi.tar.xz?rev=17baf091942042768d55c9a304610954&hash=06E4C2BB7EBE7C70EA4EA51ABF9AAE2D
```

Unfortunately this will not work with Conan. This URL actually performs a
redirection, which resolves to the actual file to be downloaded. We want that
redirected URL. To get that URL run this through the `wget` command you get
output like this:

```bash
wget "https://developer.arm.com/-/media/Files/downloads/gnu/13.2.rel1/binrel/arm-gnu-toolchain-13.2.rel1-aarch64-arm-none-eabi.tar.xz\?rev\=17baf091942042768d55c9a304610954\&hash\=06E4C2BB7EBE7C70EA4EA51ABF9AAE2D"
```

```plaintext
--2025-03-10 12:23:33--  https://developer.arm.com/-/media/Files/downloads/gnu/13.2.rel1/binrel/arm-gnu-toolchain-13.2.rel1-aarch64-arm-none-eabi.tar.xz?rev=17baf091942042768d55c9a304610954&hash=06E4C2BB7EBE7C70EA4EA51ABF9AAE2D
Resolving developer.arm.com (developer.arm.com)... 23.67.33.42, 23.67.33.47
Connecting to developer.arm.com (developer.arm.com)|23.67.33.42|:443... connected.
HTTP request sent, awaiting response... 302 Moved Temporarily
Location: https://armkeil.blob.core.windows.net/developer/Files/downloads/gnu/13.2.rel1/binrel/arm-gnu-toolchain-13.2.rel1-aarch64-arm-none-eabi.tar.xz [following]
--2025-03-10 12:23:33--  https://armkeil.blob.core.windows.net/developer/Files/downloads/gnu/13.2.rel1/binrel/arm-gnu-toolchain-13.2.rel1-aarch64-arm-none-eabi.tar.xz
Resolving armkeil.blob.core.windows.net (armkeil.blob.core.windows.net)... 20.209.15.139
Connecting to armkeil.blob.core.windows.net (armkeil.blob.core.windows.net)|20.209.15.139|:443... connected.
HTTP request sent, awaiting response... 200 OK
Length: 176409124 (168M) [application/octet-stream]
Saving to: ‘arm-gnu-toolchain-13.2.rel1-aarch64-arm-none-eabi.tar.xz?rev=17baf091942042768d55c9a304610954&hash=06E4C2BB7EBE7C70EA4EA51ABF9AAE2D’
```

The line starting with `Location:` holds the desired URL. Take that URL and put
it under the corresponding OS and Architecture. In this case, the URL would be
put under `Linux` and `armv8`.

In order to get a sha256 sum, allow the wget command to complete and run the
following on the command:

```bash
shasum -a 256 <insert file name>
```

Install this or the equivalent for your machine.
