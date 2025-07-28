#!/bin/bash
set -e

# Set up Python environment
if [ ! -d "venv" ]; then
    brew install python@3.11
    echo "Setting up Python environment..."
    python3.11 -m venv venv
fi
source venv/bin/activate

# Install system dependencies
echo "Installing system dependencies..."
brew install cmake ninja
brew link cmake
pip install "conan<2.0"

conan profile update settings.compiler.version=16 default

# We'll build Python bindings locally instead of installing pre-built griddly

# Update dependencies configuration
echo "Updating dependencies configuration..."
cat > deps/conanfile.txt << 'EOF'
[requires]
gtest/1.11.0
shaderc/2021.1
pybind11/2.10.0
glm/0.9.9.8
yaml-cpp/0.6.3
spdlog/1.9.2
stb/20200203
volk/1.3.243.0
boost/1.83.0

[generators]
CMakeToolchain
CMakeDeps
cmake_paths

[options]
boost:shared=False
boost:without_random=False
boost:without_atomic=True
boost:without_chrono=True
boost:without_container=True
boost:without_context=True
boost:without_contract=True
boost:without_coroutine=True
boost:without_date_time=True
boost:without_exception=True
boost:without_fiber=True
boost:without_filesystem=True
boost:without_graph=True
boost:without_graph_parallel=True
boost:without_iostreams=True
boost:without_json=True
boost:without_locale=True
boost:without_log=True
boost:without_math=True
boost:without_mpi=True
boost:without_nowide=True
boost:without_program_options=False
boost:without_python=True
boost:without_regex=True
boost:without_serialization=True
boost:without_stacktrace=True
boost:without_system=False
boost:without_test=True
boost:without_thread=True
boost:without_timer=True
boost:without_type_erasure=True
boost:without_url=True
boost:without_wave=True
EOF

# Check CMake version and downgrade if necessary
echo "Checking CMake version..."
CMAKE_VERSION=$(cmake --version | head -n 1 | awk '{print $3}')
CMAKE_MAJOR=$(echo $CMAKE_VERSION | cut -d. -f1)

if [ "$CMAKE_MAJOR" -ge 4 ]; then
    echo "CMake $CMAKE_VERSION detected, downgrading to 3.30.5..."
    if [ ! -d "cmake-3.30.5-macos-universal" ]; then
        curl -L -O https://github.com/Kitware/CMake/releases/download/v3.30.5/cmake-3.30.5-macos-universal.tar.gz
        tar -xzf cmake-3.30.5-macos-universal.tar.gz
    fi
    export PATH="$(pwd)/cmake-3.30.5-macos-universal/CMake.app/Contents/bin:$PATH"
    echo "Using CMake $(cmake --version | head -n 1 | awk '{print $3}')"
fi

# Configure dependencies
echo "Configuring dependencies..."
export PATH="$(pwd)/cmake-3.30.5-macos-universal/CMake.app/Contents/bin:$PATH"
./configure.sh -b=Debug

# Configure CMake build
echo "Configuring CMake build..."
export PATH="$(pwd)/cmake-3.30.5-macos-universal/CMake.app/Contents/bin:$PATH"

# Set Python paths for the build
PYTHON_PATH=$(which python)
PYTHON_VERSION=$(python -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')")
PYTHON_INCLUDE_DIR=$(python -c "from distutils.sysconfig import get_python_inc; print(get_python_inc())")

echo "Using Python: $PYTHON_PATH"
echo "Python version: $PYTHON_VERSION"
echo "Python include dir: $PYTHON_INCLUDE_DIR"

cmake . -B build -GNinja \
  -DCMAKE_BUILD_TYPE=Debug \
  -DCMAKE_TOOLCHAIN_FILE=build/conan_toolchain.cmake \
  -DENABLE_PYTHON_BINDINGS=ON \
  -DWARNINGS_AS_ERRORS=OFF \
  -DPYTHON_EXECUTABLE="$PYTHON_PATH" \
  -DPYTHON_INCLUDE_DIR="$PYTHON_INCLUDE_DIR"

# Build the project
echo "Building C++ binaries..."
export PATH="$(pwd)/cmake-3.30.5-macos-universal/CMake.app/Contents/bin:$PATH"
cmake --build build --config Debug -j8

# Install Python development package (skip if Python bindings are disabled)
echo "Checking if Python bindings were built..."
if [ -f "Debug/bin/python_griddly"* ] 2>/dev/null || [ -f "Release/bin/python_griddly"* ] 2>/dev/null; then
    echo "Installing Python development package..."
    cd python
    pip install -e .
    cd ..
else
    echo "Python bindings not found - skipping Python package installation"
    echo "C++ binaries are available for linking"
fi

echo "Build complete! Binaries are available in Debug/bin/"
ls -la Debug/bin/

rm -rf cmake-3.30.5-macos-universal.tar.gz