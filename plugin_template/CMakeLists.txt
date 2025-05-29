cmake_minimum_required(VERSION 3.22 FATAL_ERROR)

project(Boiler_plate VERSION 0.1.0)

set(CMAKE_CXX_STANDARD 20)
add_subdirectory(../../libs/juce ./juce)
add_subdirectory(plugin)