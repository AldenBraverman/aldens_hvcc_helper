/*
  ==============================================================================

    This file contains the basic framework code for a JUCE plugin editor.

  ==============================================================================
*/

#include "Boiler_plate/PluginProcessor.h"
#include "Boiler_plate/PluginEditor.h"

namespace Boiler_plate {
  namespace {
    auto streamToVector (juce::InputStream& stream)
    {
        using namespace juce;
        std::vector<std::byte> result ((size_t) stream.getTotalLength());
        stream.setPosition (0);
        [[maybe_unused]] const auto bytesRead = stream.read (result.data(), result.size());
        jassert (bytesRead == (ssize_t) result.size());
        return result;
    }

    const char* getMimeForExtension (const juce::String& extension)
    {
        using namespace juce;
        static const std::unordered_map<String, const char*> mimeMap =
        {
            { { "htm"   },  "text/html"                },
            { { "html"  },  "text/html"                },
            { { "txt"   },  "text/plain"               },
            { { "jpg"   },  "image/jpeg"               },
            { { "jpeg"  },  "image/jpeg"               },
            { { "svg"   },  "image/svg+xml"            },
            { { "ico"   },  "image/vnd.microsoft.icon" },
            { { "json"  },  "application/json"         },
            { { "png"   },  "image/png"                },
            { { "css"   },  "text/css"                 },
            { { "map"   },  "application/json"         },
            { { "js"    },  "text/javascript"          },
            { { "woff2" },  "font/woff2"               }
        };

        if (const auto it = mimeMap.find (extension.toLowerCase()); it != mimeMap.end())
            return it->second;

        jassertfalse;
        return "";
    }
  }
  //==============================================================================
  AudioPluginAudioProcessorEditor::AudioPluginAudioProcessorEditor (AudioPluginAudioProcessor& p)
      : AudioProcessorEditor (&p), audioProcessor (p)
  {
      // Make sure that before the constructor has finished, you've set the
      // editor's size to whatever you need it to be.
      setSize (400, 300);
  }

  AudioPluginAudioProcessorEditor::~AudioPluginAudioProcessorEditor()
  {
  }

  //==============================================================================
  void AudioPluginAudioProcessorEditor::paint (juce::Graphics& g)
  {
      // (Our component is opaque, so we must completely fill the background with a solid colour)
      g.fillAll (getLookAndFeel().findColour (juce::ResizableWindow::backgroundColourId));

      g.setColour (juce::Colours::white);
      g.setFont (juce::FontOptions (15.0f));
      g.drawFittedText ("Hello World!", getLocalBounds(), juce::Justification::centred, 1);
  }

  void AudioPluginAudioProcessorEditor::resized()
  {
      // This is generally where you'll want to lay out the positions of any
      // subcomponents in your editor..
  }
}