juce_add_plugin(JuceWebViewPlugin
    COMPANY_NAME aldenbraverman
    IS_SYNTH FALSE
    NEEDS_MIDI_INPUT FALSE
    NEEDS_MIDI_OUTPUT FALSE
    PLUGIN_MANUFACTURER_CODE ALDB
    PLUGIN_CODE ALDB
    FORMATS AU VST3 Standalone
    NEEDS_WEBVIEW2 TRUE
)

get_target_property(PRODUCT_NAME JuceWebViewPlugin JUCE_PRODUCT_NAME)
get_target_property(COMPANY_NAME JuceWebViewPlugin JUCE_COMPANY_NAME)
target_compile_definitions(JuceWebViewPlugin PRIVATE
    JUCE_PRODUCT_NAME="${PRODUCT_NAME}"
    JUCE_COMPANY_NAME="${COMPANY_NAME}"
    JUCE_PRODUCT_VERSION="${PROJECT_VERSION}"
)

target_sources(JuceWebViewPlugin
    PRIVATE src/PluginEditor.cpp src/PluginProcessor.cpp)

target_include_directories(JuceWebViewPlugin PRIVATE include)

target_link_libraries(JuceWebViewPlugin
    PRIVATE
        juce::juce_audio_utils
        asio
    PUBLIC
        juce::juce_recommended_config_flags
        juce::juce_recommended_lto_flags
        juce::juce_recommended_warning_flags
)

target_compile_definitions(JuceWebViewPlugin
    PUBLIC 
        JUCE_WEB_BROWSER=1
        JUCE_USE_CURL=0
        JUCE_VST3_CAN_REPLACE_VST2=0
        JUCE_USE_WIN_WEBVIEW2_WITH_STATIC_LINKING=1
)

# file(COPY "${EXTERNAL_JUCE_LIB_PATH}/modules/juce_gui_extra/native/javascript/" DESTINATION "${CMAKE_CURRENT_SOURCE_DIR}/ui/public/js/juce/")