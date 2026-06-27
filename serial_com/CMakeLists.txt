cmake_minimum_required(VERSION 4.0)
project(serial_com)

set(CMAKE_CXX_STANDARD 20)

add_executable(serial_com main.cpp)

include(FetchContent)
FetchContent_Declare(
        serialpp
        URL https://github.com/IFSCEngtelecomPTC/SerialPP/archive/refs/tags/v1.0.0.tar.gz
)
FetchContent_MakeAvailable(serialpp)
include_directories(${serialpp_SOURCE_DIR} .)

include(FetchContent)
FetchContent_Declare(
        poller
        URL https://github.com/IFSCEngtelecomPTC/Poller/archive/refs/tags/v1.0.1.tar.gz
)
FetchContent_MakeAvailable(poller)
include_directories(${poller_SOURCE_DIR} .)

# OBS: this is just a demo to show you how to link this library to your executable

# This command links socketpp library to your executable
# Rename test_app to yout executable name
target_link_libraries(serial_com SerialPP poller)