/*
  ==============================================================================

    This file contains the basic framework code for a JUCE plugin processor.

  ==============================================================================
*/

#pragma once
#include <juce_audio_processors/juce_audio_processors.h>
#include "Heavy_Boiler_plate.h"

namespace ParameterID
{
    #define PARAMETER_ID(str) const juce::ParameterID str(#str, 1);
    // Parameters go here like this: PARAMETER_ID(param)
    // @_PARAM_IDS_GO_HERE

    #undef PARAMETER_ID
}

//==============================================================================
namespace Boiler_plate {
  class AudioPluginAudioProcessor  : public juce::AudioProcessor, private juce::ValueTree::Listener
  {
  public:
      //==============================================================================
      AudioPluginAudioProcessor();
      ~AudioPluginAudioProcessor() override;

      //==============================================================================
      void prepareToPlay (double sampleRate, int samplesPerBlock) override;
      void releaseResources() override;

    #ifndef JucePlugin_PreferredChannelConfigurations
      bool isBusesLayoutSupported (const BusesLayout& layouts) const override;
    #endif

      void processBlock (juce::AudioBuffer<float>&, juce::MidiBuffer&) override;

      //==============================================================================
      juce::AudioProcessorEditor* createEditor() override;
      bool hasEditor() const override;

      //==============================================================================
      const juce::String getName() const override;

      bool acceptsMidi() const override;
      bool producesMidi() const override;
      bool isMidiEffect() const override;
      double getTailLengthSeconds() const override;

      //==============================================================================
      int getNumPrograms() override;
      int getCurrentProgram() override;
      void setCurrentProgram (int index) override;
      const juce::String getProgramName (int index) override;
      void changeProgramName (int index, const juce::String& newName) override;

      //==============================================================================
      void getStateInformation (juce::MemoryBlock& destData) override;
      void setStateInformation (const void* data, int sizeInBytes) override;

      // juce::AudioProcessorValueTreeState apvts {*this, nullptr, "Parameters", createParameterLayout() };

      // @_PLACE_PARAMS_HERE

  private:
      // juce::AudioProcessorValueTreeState::ParameterLayout createParameterLayout();
          
      std::atomic<bool> parametersChanged { false };
      void valueTreePropertyChanged(juce::ValueTree&, const juce::Identifier&) override
      {
          parametersChanged.store(true);
      }

      void update();
      //==============================================================================
      JUCE_DECLARE_NON_COPYABLE_WITH_LEAK_DETECTOR (AudioPluginAudioProcessor)
  };
}