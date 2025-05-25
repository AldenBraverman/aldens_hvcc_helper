juce_add_plugin(Boiler_plate
    COMPANY_NAME aldenbraverman
    IS_SYNTH FALSE
    NEEDS_MIDI_INPUT FALSE
    NEEDS_MIDI_OUTPUT FALSE
    PLUGIN_MANUFACTURER_CODE ALDB
    PLUGIN_CODE ALDB
    FORMATS AU VST3 Standalone
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
    PRIVATE src/PluginEditor.cpp src/PluginProcessor.cpp ${CMAKE_SOURCE_DIR}/Heavy/c/Heavy_Boiler_plate.cpp ${CMAKE_SOURCE_DIR}/Heavy/c/HeavyContext.cpp ${CMAKE_SOURCE_DIR}/Heavy/c/HvHeavy.cpp ${CMAKE_SOURCE_DIR}/Heavy/c/HvControlBinop.c ${CMAKE_SOURCE_DIR}/Heavy/c/HvControlCast.c ${CMAKE_SOURCE_DIR}/Heavy/c/HvControlDelay.c ${CMAKE_SOURCE_DIR}/Heavy/c/HvControlIf.c ${CMAKE_SOURCE_DIR}/Heavy/c/HvControlPack.c ${CMAKE_SOURCE_DIR}/Heavy/c/HvControlSlice.c ${CMAKE_SOURCE_DIR}/Heavy/c/HvControlSystem.c ${CMAKE_SOURCE_DIR}/Heavy/c/HvControlTabread.c ${CMAKE_SOURCE_DIR}/Heavy/c/HvControlTabwrite.c ${CMAKE_SOURCE_DIR}/Heavy/c/HvControlUnop.c ${CMAKE_SOURCE_DIR}/Heavy/c/HvControlVar.c ${CMAKE_SOURCE_DIR}/Heavy/c/HvLightPipe.c ${CMAKE_SOURCE_DIR}/Heavy/c/HvMessage.c ${CMAKE_SOURCE_DIR}/Heavy/c/HvMessagePool.c ${CMAKE_SOURCE_DIR}/Heavy/c/HvMessageQueue.c ${CMAKE_SOURCE_DIR}/Heavy/c/HvSignalDel1.c ${CMAKE_SOURCE_DIR}/Heavy/c/HvSignalLine.c ${CMAKE_SOURCE_DIR}/Heavy/c/HvSignalPhasor.c ${CMAKE_SOURCE_DIR}/Heavy/c/HvSignalSamphold.c ${CMAKE_SOURCE_DIR}/Heavy/c/HvSignalVar.c ${CMAKE_SOURCE_DIR}/Heavy/c/HvTable.c ${CMAKE_SOURCE_DIR}/Heavy/c/HvUtils.c)

target_include_directories(Boiler_plate PRIVATE include ${CMAKE_SOURCE_DIR}/Heavy/h)

# add_library(hvcc_c INTERFACE)
# target_include_directories(hvcc_c INTERFACE ${CMAKE_SOURCE_DIR}/Heavy/c)

target_link_libraries(Boiler_plate
    PRIVATE
        juce::juce_audio_utils
        # hvcc_c
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

# file(COPY "${EXTERNAL_JUCE_LIB_PATH}/modules/juce_gui_extra/native/javascript/" DESTINATION "${CMAKE_CURRENT_SOURCE_DIR}/ui/public/js/juce/")