// https://chatgpt.com/c/67b382d4-1614-8012-8bad-7b18ec8dd8b0

import { useState, useEffect } from "react";
import { Slider, Typography, Box } from "@mui/material";

export default function VolumeSlider() {
  const [sliderValue, setSliderValue] = useState(0.05);

  useEffect(() => {
    // Hide the HTML slider when React component mounts
    const htmlSliderContainer = document.querySelector(".parameter-slider");
    if (htmlSliderContainer) {
      htmlSliderContainer.style.display = "none";
    }
  }, []);

  const handleChange = (event, newValue) => {
    setSliderValue(newValue);

    // Update the hidden HTML input slider
    const htmlSlider = document.getElementById("parameter_vol");
    if (htmlSlider) {
      htmlSlider.value = newValue;
      updateSlider_vol(newValue);
    }
  };

  return (
    <Box display="flex" flexDirection="column" alignItems="center" width={200}>
      <Typography variant="body1">Volume: {sliderValue.toFixed(3)}</Typography>
      <Slider
        value={sliderValue}
        min={0}
        max={0.1}
        step={0.001}
        onChange={handleChange}
        aria-labelledby="volume-slider"
      />
    </Box>
  );
}
