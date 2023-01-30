# Steps to Test

```
mkdir build
cd build
conan create ..
```

If you are Linux/Mac run:

```
source activate_run.sh
```

On Windows run:

```
source activate_run.sh # on windows
```

Now you should be able to run `arm-none-eabi-g++` and get the following output.

```
$ arm-none-eabi-g++
arm-none-eabi-g++: fatal error: no input files
compilation terminated.
```
