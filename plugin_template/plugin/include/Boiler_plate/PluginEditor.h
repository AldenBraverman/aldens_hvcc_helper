#pragma once
// #include <JuceHeader.h>
#include "Boiler_plate/PluginProcessor.h"
#include <juce_gui_extra/juce_gui_extra.h>

//==============================================================================
namespace Boiler_plate {
  class AudioPluginAudioProcessorEditor  : public juce::AudioProcessorEditor
  {
  public:
    AudioPluginAudioProcessorEditor (AudioPluginAudioProcessor&);
    ~AudioPluginAudioProcessorEditor() override;

    //==============================================================================
    void paint (juce::Graphics&) override;
    void resized() override;

  private:
    // This reference is provided as a quick way for your editor to
    // access the processor object that created it.
    AudioPluginAudioProcessor& audioProcessor;

    JUCE_DECLARE_NON_COPYABLE_WITH_LEAK_DETECTOR (AudioPluginAudioProcessorEditor)
  };
}