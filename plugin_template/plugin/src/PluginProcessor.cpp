/*
  ==============================================================================

    This file contains the basic framework code for a JUCE plugin processor.

  ==============================================================================
*/

#include "Boiler_plate/PluginProcessor.h"
#include "Boiler_plate/PluginEditor.h"
#include "Boiler_plate/Utils.h"

namespace Boiler_plate {
    //==============================================================================
    AudioPluginAudioProcessor::AudioPluginAudioProcessor()
    #ifndef JucePlugin_PreferredChannelConfigurations
        : AudioProcessor (BusesProperties()
                        #if ! JucePlugin_IsMidiEffect
                        #if ! JucePlugin_IsSynth
                        .withInput  ("Input",  juce::AudioChannelSet::stereo(), true)
                        #endif
                        .withOutput ("Output", juce::AudioChannelSet::stereo(), true)
                        #endif
                        )
    #endif
    {
        context = hv_Boiler_plate_new(44100.0);
        // @_ADD_CAST_PARAMETERS_HERE

        apvts.state.addListener(this);
    }

    AudioPluginAudioProcessor::~AudioPluginAudioProcessor()
    {
        hv_delete(context);
        
        apvts.state.removeListener(this);
    }

    //==============================================================================
    const juce::String AudioPluginAudioProcessor::getName() const
    {
        return JucePlugin_Name;
    }

    bool AudioPluginAudioProcessor::acceptsMidi() const
    {
    #if JucePlugin_WantsMidiInput
        return true;
    #else
        return false;
    #endif
    }

    bool AudioPluginAudioProcessor::producesMidi() const
    {
    #if JucePlugin_ProducesMidiOutput
        return true;
    #else
        return false;
    #endif
    }

    bool AudioPluginAudioProcessor::isMidiEffect() const
    {
    #if JucePlugin_IsMidiEffect
        return true;
    #else
        return false;
    #endif
    }

    double AudioPluginAudioProcessor::getTailLengthSeconds() const
    {
        return 0.0;
    }

    int AudioPluginAudioProcessor::getNumPrograms()
    {
        return 1;   // NB: some hosts don't cope very well if you tell them there are 0 programs,
                    // so this should be at least 1, even if you're not really implementing programs.
    }

    int AudioPluginAudioProcessor::getCurrentProgram()
    {
        return 0;
    }

    void AudioPluginAudioProcessor::setCurrentProgram (int index)
    {
    }

    const juce::String AudioPluginAudioProcessor::getProgramName (int index)
    {
        return {};
    }

    void AudioPluginAudioProcessor::changeProgramName (int index, const juce::String& newName)
    {
    }

    //==============================================================================
    void AudioPluginAudioProcessor::prepareToPlay (double sampleRate, int samplesPerBlock)
    {
        // Use this method as the place to do any pre-playback
        // initialisation that you need..
        if (hv_getSampleRate(context) != sampleRate)
        {
            if (context != nullptr) hv_delete(context);

            // @_ADD_HEAVY_CONTEXT_HERE
            context = hv_osc_one_d_one_new(sampleRate);
        }
        
        parametersChanged.store(true);
    }

    void AudioPluginAudioProcessor::update()
    {
        // @_ADD_PARAMS_TO_UPDATE_HERE
        // float _volValue = volParam->get();
        // hv_sendFloatToReceiver(context, 0x8559698F, _volValue);
    }

    void AudioPluginAudioProcessor::releaseResources()
    {
        // When playback stops, you can use this as an opportunity to free up any
        // spare memory, etc.
    }

    #ifndef JucePlugin_PreferredChannelConfigurations
    bool AudioPluginAudioProcessor::isBusesLayoutSupported (const BusesLayout& layouts) const
    {
    #if JucePlugin_IsMidiEffect
        juce::ignoreUnused (layouts);
        return true;
    #else
        // This is the place where you check if the layout is supported.
        // In this template code we only support mono or stereo.
        // Some plugin hosts, such as certain GarageBand versions, will only
        // load plugins that support stereo bus layouts.
        if (layouts.getMainOutputChannelSet() != juce::AudioChannelSet::mono()
        && layouts.getMainOutputChannelSet() != juce::AudioChannelSet::stereo())
            return false;

        // This checks if the input layout matches the output layout
    #if ! JucePlugin_IsSynth
        if (layouts.getMainOutputChannelSet() != layouts.getMainInputChannelSet())
            return false;
    #endif

        return true;
    #endif
    }
    #endif

    void AudioPluginAudioProcessor::processBlock (juce::AudioBuffer<float>& buffer, juce::MidiBuffer& midiMessages)
    {
        bool expected = true;
        if (isNonRealtime() || parametersChanged.compare_exchange_strong(expected, false)) {
            update();
        }

        juce::ScopedNoDenormals noDenormals;
        auto totalNumInputChannels  = getTotalNumInputChannels();
        auto totalNumOutputChannels = getTotalNumOutputChannels();

        // In case we have more outputs than inputs, this code clears any output
        // channels that didn't contain input data, (because these aren't
        // guaranteed to be empty - they may contain garbage).
        // This is here to avoid people getting screaming feedback
        // when they first compile a plugin, but obviously you don't need to keep
        // this code if your algorithm always overwrites all the output channels.
        for (auto i = totalNumInputChannels; i < totalNumOutputChannels; ++i)
        buffer.clear (i, 0, buffer.getNumSamples());

        float* outputBuffers[2] = { nullptr, nullptr };
        float* inputBuffers[2] = { nullptr, nullptr };

        outputBuffers[0] = buffer.getWritePointer(0);
        inputBuffers[0] = buffer.getWritePointer(0);
        
        if (getTotalNumOutputChannels() > 1) {
            outputBuffers[1] = buffer.getWritePointer(1);
            inputBuffers[1] = buffer.getWritePointer(1);
        }
        
        hv_process(context, nullptr, outputBuffers, buffer.getNumSamples());
        
        splitBufferByEvents(buffer, midiMessages);
    }

    void AudioPluginAudioProcessor::splitBufferByEvents(juce::AudioBuffer<float>& buffer, juce::MidiBuffer& midiMessages)
    {
        int bufferOffset = 0;

        // Loop through the MIDI messages, which are sorted by samplePosition.
        for (const auto metadata : midiMessages) {

            // Render the audio that happens before this event (if any).
            int samplesThisSegment = metadata.samplePosition - bufferOffset;
            if (samplesThisSegment > 0) {
                // render(buffer, samplesThisSegment, bufferOffset);
                bufferOffset += samplesThisSegment;
            }

            // Handle the event. Ignore MIDI messages such as sysex.
            if (metadata.numBytes <= 3) {
                uint8_t data1 = (metadata.numBytes >= 2) ? metadata.data[1] : 0;
                uint8_t data2 = (metadata.numBytes == 3) ? metadata.data[2] : 0;
                handleMIDI(metadata.data[0], data1, data2);
            }
        }

        // Render the audio after the last MIDI event. If there were no
        // MIDI events at all, this renders the entire buffer.
        int samplesLastSegment = buffer.getNumSamples() - bufferOffset;
        if (samplesLastSegment > 0) {
            // render(buffer, samplesLastSegment, bufferOffset);
        }

        midiMessages.clear();
    }

    void AudioPluginAudioProcessor::handleMIDI(uint8_t data0, uint8_t data1, uint8_t data2)
    {
        switch (data0 & 0xF0) {
            // Note off
            case 0x80:
                noteOff(data1 & 0x7F);
                break;

            // Note on
            case 0x90: {
                uint8_t note = data1 & 0x7F;
                uint8_t velo = data2 & 0x7F;
                if (velo > 0) {
                    noteOn(note, velo);
                } else {
                    noteOff(note);
                }
                break;
            }
        }
    }

    void AudioPluginAudioProcessor::noteOn(int note, int velocity)
    {
        // @_UNCOMMENT_NOTE_ON_HERE
        // context->sendMessageToReceiverV(0x67E37CA3, 0, "fff", (float) note, (float) velocity, 1.0f);
    }

    void AudioPluginAudioProcessor::noteOff(int note)
    {
        // @_UNCOMMENT_NOTE_OFF_HERE
        // context->sendMessageToReceiverV(0x67E37CA3, 0, "fff", (float) note, 0.0f, 1.0f);
    }

    //==============================================================================
    bool AudioPluginAudioProcessor::hasEditor() const
    {
        return true; // (change this to false if you choose to not supply an editor)
    }

    juce::AudioProcessorEditor* AudioPluginAudioProcessor::createEditor()
    {
        // return new AudioPluginAudioProcessorEditor (*this);

        // Generic UI
        auto editor = new juce::GenericAudioProcessorEditor(*this);
        editor->setSize(500, 250);
        return editor;
    }

    //==============================================================================
    void AudioPluginAudioProcessor::getStateInformation (juce::MemoryBlock& destData)
    {
        // You should use this method to store your parameters in the memory block.
        // You could do that either as raw data, or use the XML or ValueTree classes
        // as intermediaries to make it easy to save and load complex data.
    }

    void AudioPluginAudioProcessor::setStateInformation (const void* data, int sizeInBytes)
    {
        // You should use this method to restore your parameters from this memory block,
        // whose contents will have been created by the getStateInformation() call.
    }

    juce::AudioProcessorValueTreeState::ParameterLayout AudioPluginAudioProcessor::createParameterLayout()
    {
        juce::AudioProcessorValueTreeState::ParameterLayout layout;
        // @_LAYOUT_PARAM_IDS_GO_HERE
        return layout;
    }
}

juce::AudioProcessor* JUCE_CALLTYPE createPluginFilter()
{
    return new Boiler_plate::AudioPluginAudioProcessor();
}