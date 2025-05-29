import React, { useState } from "react";
import ReactDOM from "react-dom";
import VolumeSlider from "./VolumeSlider";
import PowerSwitchComponent from "./PowerSwitch";
import { CssBaseline, Container } from "@mui/material";
import { ThemeProvider, createTheme } from '@mui/material/styles';

const theme = createTheme({
  palette: {
    error: {
      main: '#f44336',
    },
    success: {
      main: '#4caf50',
    },
  },
});

function App() {
  const [volume, setVolume] = useState(0.05);
  const [checked, setChecked] = React.useState(false);

  const handleChange = (event) => {
    setChecked(event.target.checked);
  };

  const handleToggle = (isChecked) => {
    const transportButton = document.getElementById('transportButton');
    if (transportButton) {
      transportButton.checked = isChecked;
      transportButton.dispatchEvent(new Event('change'));
    }
  };

  return (
    <Container maxWidth="sm" style={{ textAlign: "center", marginTop: "50px" }}>
      <CssBaseline />
      <h1>Material UI Slider Example</h1>
      <VolumeSlider value={volume} onChange={setVolume} />
      <ThemeProvider theme={theme}>
        <PowerSwitchComponent checked={checked} onChange={handleChange} onToggle={handleToggle} />
      </ThemeProvider>
    </Container>
  );
}

ReactDOM.render(<App />, document.getElementById("root"));
