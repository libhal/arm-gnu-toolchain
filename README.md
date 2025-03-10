# ARM GNU Toolchain Repo

Here you can find conan packages for the ARM GNU Toolchain packages used by
libhal project.

## 📦 Building & Installing the Tool Package

This conan project is a tool package. Meaning it provides binaries for tools
that the build system can rely on such as the compiler itself. This package
DOES (currently) build GCC from scratch for to cross compile for an ARM target.
Instead, this tool package simply downloads the ARM compiler from the ARM
website.

```bash
conan create . --version <insert version>
```

Install GCC 11.3 compiler into local conan cache:

```bash
conan create . --version 11.3
```

Install GCC 12.2 compiler into local conan cache:

```bash
conan create . --version 12.2
```

Install GCC 12.3 compiler into local conan cache:

```bash
conan create . --version 12.3
```

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
