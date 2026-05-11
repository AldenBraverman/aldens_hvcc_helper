/*
  ==============================================================================

    JUCE processor embedding Pure Data via libpd.

  ==============================================================================
*/

#pragma once
#include <juce_audio_processors/juce_audio_processors.h>

namespace ParameterID
{
    #define PARAMETER_ID(str) const juce::ParameterID str(#str, 1);
    #undef PARAMETER_ID
}

//==============================================================================
namespace Boiler_plate {
class AudioPluginAudioProcessor : public juce::AudioProcessor, private juce::ValueTree::Listener
{
public:
    AudioPluginAudioProcessor();
    ~AudioPluginAudioProcessor() override;

    void prepareToPlay (double sampleRate, int samplesPerBlock) override;
    void releaseResources() override;

#ifndef JucePlugin_PreferredChannelConfigurations
    bool isBusesLayoutSupported (const BusesLayout& layouts) const override;
#endif

    void processBlock (juce::AudioBuffer<float>&, juce::MidiBuffer&) override;

    juce::AudioProcessorEditor* createEditor() override;
    bool hasEditor() const override;

    const juce::String getName() const override;

    bool acceptsMidi() const override;
    bool producesMidi() const override;
    bool isMidiEffect() const override;
    double getTailLengthSeconds() const override;

    int getNumPrograms() override;
    int getCurrentProgram() override;
    void setCurrentProgram (int index) override;
    const juce::String getProgramName (int index) override;
    void changeProgramName (int index, const juce::String& newName) override;

    void getStateInformation (juce::MemoryBlock& destData) override;
    void setStateInformation (const void* data, int sizeInBytes) override;

    juce::AudioProcessorValueTreeState apvts { *this, nullptr, "Parameters", createParameterLayout() };

private:
    juce::AudioProcessorValueTreeState::ParameterLayout createParameterLayout();

    std::atomic<bool> parametersChanged { false };
    void valueTreePropertyChanged (juce::ValueTree&, const juce::Identifier&) override
    {
        parametersChanged.store (true);
    }

    void update();
    void closePatch();
    void drainMidi (juce::MidiBuffer& midiMessages);
    void handleMIDI (uint8_t data0, uint8_t data1, uint8_t data2);
    void noteOn (int note, int velocity);
    void noteOff (int note);

    void* pdPatch = nullptr;
    juce::File pdTempDir;
    double currentSampleRate = 44100.0;

    JUCE_DECLARE_NON_COPYABLE_WITH_LEAK_DETECTOR (AudioPluginAudioProcessor)
};
} // namespace Boiler_plate
