cmake_minimum_required(VERSION 3.22 FATAL_ERROR)

project(JuceWebViewPlugin VERSION 0.1.0)

set(CMAKE_CXX_STANDARD 20)
add_subdirectory(${EXTERNAL_JUCE_LIB_PATH})
add_subdirectory(plugin)