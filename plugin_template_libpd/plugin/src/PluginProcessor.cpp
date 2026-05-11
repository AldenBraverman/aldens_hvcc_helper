/*
  ==============================================================================

    JUCE plugin processor using libpd (desktop). Audio is processed in blocks of
    libpd_blocksize() samples; any tail shorter than a full block is passed through.

  ==============================================================================
*/

#include "Boiler_plate/PluginProcessor.h"
#include "LibPdBinaryData.h"

#include <vector>

extern "C" {
#include "z_libpd.h"
}

namespace
{
std::once_flag gLibPdInitFlag;

void writeEmbeddedPdFiles (const juce::File& dir)
{
    using namespace LibPdEmbed;
    for (int i = 0; i < namedResourceListSize; ++i)
    {
        const char* resName = namedResourceList[i];
        int numBytes = 0;
        const char* data = getNamedResource (resName, numBytes);
        if (data == nullptr || numBytes <= 0)
            continue;

        const char* orig = getNamedResourceOriginalFilename (resName);
        juce::String rel (orig != nullptr ? orig : resName);
        auto out = dir.getChildFile (rel);
        out.getParentDirectory().createDirectory();
        out.replaceWithData (data, (size_t) numBytes);
    }
}
} // namespace

namespace Boiler_plate {

AudioPluginAudioProcessor::AudioPluginAudioProcessor()
#ifndef JucePlugin_PreferredChannelConfigurations
    : AudioProcessor (BusesProperties()
#if ! JucePlugin_IsMidiEffect
#if ! JucePlugin_IsSynth
                          .withInput ("Input", juce::AudioChannelSet::stereo(), true)
#endif
                          .withOutput ("Output", juce::AudioChannelSet::stereo(), true)
#endif
                      )
#endif
{
    apvts.state.addListener (this);
}

AudioPluginAudioProcessor::~AudioPluginAudioProcessor()
{
    closePatch();
    apvts.state.removeListener (this);
}

void AudioPluginAudioProcessor::closePatch()
{
    if (pdPatch != nullptr)
    {
        libpd_closefile (pdPatch);
        pdPatch = nullptr;
    }

    if (pdTempDir.isDirectory())
        pdTempDir.deleteRecursively();
    pdTempDir = juce::File();
}

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
    return 1;
}

int AudioPluginAudioProcessor::getCurrentProgram()
{
    return 0;
}

void AudioPluginAudioProcessor::setCurrentProgram (int) {}

const juce::String AudioPluginAudioProcessor::getProgramName (int)
{
    return {};
}

void AudioPluginAudioProcessor::changeProgramName (int, const juce::String&) {}

void AudioPluginAudioProcessor::prepareToPlay (double sampleRate, int)
{
    currentSampleRate = sampleRate;

    std::call_once (gLibPdInitFlag, [] { libpd_init(); });

    closePatch();

    pdTempDir = juce::File::getSpecialLocation (juce::File::tempDirectory)
                    .getChildFile ("aldens_libpd_" + juce::String (juce::Random::getSystemRandom().nextInt64()));

    if (! pdTempDir.createDirectory())
        return;

    writeEmbeddedPdFiles (pdTempDir);

    libpd_clear_search_path();
    libpd_add_to_search_path (pdTempDir.getFullPathName().toRawUTF8());

    if (libpd_init_audio (2, 2, (int) currentSampleRate) != 0)
        return;

    juce::Array<juce::File> mainCandidates;
    pdTempDir.findChildFiles (mainCandidates, juce::File::findFiles, true, "main.pd");
    if (mainCandidates.isEmpty())
        return;

    const juce::File mainFile = mainCandidates.getReference (0);
    pdPatch = libpd_openfile (mainFile.getFileName().toRawUTF8(),
                              mainFile.getParentDirectory().getFullPathName().toRawUTF8());
}

void AudioPluginAudioProcessor::update() {}

void AudioPluginAudioProcessor::releaseResources() {}

#ifndef JucePlugin_PreferredChannelConfigurations
bool AudioPluginAudioProcessor::isBusesLayoutSupported (const BusesLayout& layouts) const
{
#if JucePlugin_IsMidiEffect
    juce::ignoreUnused (layouts);
    return true;
#else
    if (layouts.getMainOutputChannelSet() != juce::AudioChannelSet::mono()
        && layouts.getMainOutputChannelSet() != juce::AudioChannelSet::stereo())
        return false;

#if ! JucePlugin_IsSynth
    if (layouts.getMainOutputChannelSet() != layouts.getMainInputChannelSet())
        return false;
#endif

    return true;
#endif
}
#endif

void AudioPluginAudioProcessor::drainMidi (juce::MidiBuffer& midiMessages)
{
    for (const auto metadata : midiMessages)
    {
        if (metadata.numBytes <= 3)
        {
            const uint8_t d1 = (metadata.numBytes >= 2) ? metadata.data[1] : 0;
            const uint8_t d2 = (metadata.numBytes == 3) ? metadata.data[2] : 0;
            handleMIDI (metadata.data[0], d1, d2);
        }
    }

    midiMessages.clear();
}

void AudioPluginAudioProcessor::handleMIDI (uint8_t data0, uint8_t data1, uint8_t data2)
{
    switch (data0 & 0xF0)
    {
        case 0x80:
            noteOff ((int) (data1 & 0x7F));
            break;

        case 0x90: {
            const int note = (int) (data1 & 0x7F);
            const int velo = (int) (data2 & 0x7F);
            if (velo > 0)
                noteOn (note, velo);
            else
                noteOff (note);
            break;
        }

        default:
            break;
    }
}

void AudioPluginAudioProcessor::noteOn (int note, int velocity)
{
    libpd_noteon (0, note, velocity);
}

void AudioPluginAudioProcessor::noteOff (int note)
{
    libpd_noteon (0, note, 0);
}

void AudioPluginAudioProcessor::processBlock (juce::AudioBuffer<float>& buffer, juce::MidiBuffer& midiMessages)
{
    bool expected = true;
    if (isNonRealtime() || parametersChanged.compare_exchange_strong (expected, false))
        update();

    juce::ScopedNoDenormals noDenormals;

    drainMidi (midiMessages);

    if (pdPatch == nullptr)
        return;

    const int n = buffer.getNumSamples();
    const int inch = juce::jmin (2, getTotalNumInputChannels());
    const int outch = juce::jmin (2, getTotalNumOutputChannels());
    const int bs = libpd_blocksize();

    for (auto i = inch; i < outch; ++i)
        buffer.clear (i, 0, n);

    std::vector<float> inI ((size_t) (2 * bs), 0.0f);
    std::vector<float> outI ((size_t) (2 * bs), 0.0f);

    int offset = 0;
    while (offset + bs <= n)
    {
        std::fill (inI.begin(), inI.end(), 0.0f);
        std::fill (outI.begin(), outI.end(), 0.0f);

        for (int i = 0; i < bs; ++i)
        {
            const int s = offset + i;
            const float l = inch > 0 ? buffer.getSample (0, s) : 0.0f;
            const float r = inch > 1 ? buffer.getSample (1, s) : l;
            const auto k = (size_t) (2 * i);
            inI[k] = l;
            inI[k + 1] = r;
        }

        if (libpd_process_float (1, inI.data(), outI.data()) != 0)
            return;

        for (int i = 0; i < bs; ++i)
        {
            const int s = offset + i;
            const auto k = (size_t) (2 * i);
            if (outch > 0)
                buffer.setSample (0, s, outI[k]);
            if (outch > 1)
                buffer.setSample (1, s, outI[k + 1]);
        }

        offset += bs;
    }

    if (offset < n)
    {
        for (int ch = 0; ch < outch; ++ch)
            for (int s = offset; s < n; ++s)
            {
                const float v = ch < inch ? buffer.getSample (ch, s) : 0.0f;
                buffer.setSample (ch, s, v);
            }
    }
}

bool AudioPluginAudioProcessor::hasEditor() const
{
    return true;
}

juce::AudioProcessorEditor* AudioPluginAudioProcessor::createEditor()
{
    auto* editor = new juce::GenericAudioProcessorEditor (*this);
    editor->setSize (500, 250);
    return editor;
}

void AudioPluginAudioProcessor::getStateInformation (juce::MemoryBlock&) {}

void AudioPluginAudioProcessor::setStateInformation (const void*, int) {}

juce::AudioProcessorValueTreeState::ParameterLayout AudioPluginAudioProcessor::createParameterLayout()
{
    return {};
}

} // namespace Boiler_plate

juce::AudioProcessor* JUCE_CALLTYPE createPluginFilter()
{
    return new Boiler_plate::AudioPluginAudioProcessor();
}
