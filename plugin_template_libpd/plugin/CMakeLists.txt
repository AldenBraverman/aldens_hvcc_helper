set(LIBPD_ROOT "${CMAKE_SOURCE_DIR}/../../libs/libpd")
if(NOT EXISTS "${LIBPD_ROOT}/CMakeLists.txt")
    message(FATAL_ERROR "libpd missing at ${LIBPD_ROOT}. From repo root run: git submodule update --init --recursive libs/libpd")
endif()

set(PD_BUILD_C_EXAMPLES OFF CACHE BOOL "" FORCE)
set(LIBPD_SHARED OFF CACHE BOOL "" FORCE)
set(LIBPD_STATIC ON CACHE BOOL "" FORCE)

add_subdirectory("${LIBPD_ROOT}" libpd_build)

file(GLOB_RECURSE PD_BUNDLE_FILES CONFIGURE_DEPENDS "${CMAKE_CURRENT_SOURCE_DIR}/pd/*.pd")
list(LENGTH PD_BUNDLE_FILES _pd_count)
if(_pd_count EQUAL 0)
    message(FATAL_ERROR "No Pure Data files under plugin/pd. Run tools/generate.py first.")
endif()

juce_add_binary_data(PdResources
    NAMESPACE LibPdEmbed
    HEADER_NAME LibPdBinaryData.h
    SOURCES ${PD_BUNDLE_FILES}
)

juce_add_plugin(Boiler_plate
    COMPANY_NAME aldenbraverman
    IS_SYNTH FALSE
    NEEDS_MIDI_INPUT FALSE
    NEEDS_MIDI_OUTPUT FALSE
    PLUGIN_MANUFACTURER_CODE ALDB
    PLUGIN_CODE ALDB
    FORMATS AU VST3 Standalone Unity AUv3
    NEEDS_WEBVIEW2 TRUE
)

get_target_property(PRODUCT_NAME Boiler_plate JUCE_PRODUCT_NAME)
get_target_property(COMPANY_NAME Boiler_plate JUCE_COMPANY_NAME)
target_compile_definitions(Boiler_plate PRIVATE
    JUCE_PRODUCT_NAME="${PRODUCT_NAME}"
    JUCE_COMPANY_NAME="${COMPANY_NAME}"
    JUCE_PRODUCT_VERSION="${PROJECT_VERSION}"
)

target_sources(Boiler_plate
    PRIVATE
        src/PluginEditor.cpp
        src/PluginProcessor.cpp
)

target_include_directories(Boiler_plate PRIVATE include)

target_link_libraries(Boiler_plate
    PRIVATE
        juce::juce_audio_utils
        PdResources
        libpd_static
    PUBLIC
        juce::juce_recommended_config_flags
        juce::juce_recommended_lto_flags
        juce::juce_recommended_warning_flags
)

target_compile_definitions(Boiler_plate
    PUBLIC
        JUCE_WEB_BROWSER=1
        JUCE_USE_CURL=0
        JUCE_VST3_CAN_REPLACE_VST2=0
        JUCE_USE_WIN_WEBVIEW2_WITH_STATIC_LINKING=1
)
