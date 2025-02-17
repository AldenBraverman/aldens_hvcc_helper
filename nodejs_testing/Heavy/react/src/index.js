import React, { useState } from "react";
import ReactDOM from "react-dom";
import VolumeSlider from "./VolumeSlider";
import { CssBaseline, Container } from "@mui/material";

function App() {
  const [volume, setVolume] = useState(0.05);

  return (
    <Container maxWidth="sm" style={{ textAlign: "center", marginTop: "50px" }}>
      <CssBaseline />
      <h1>Material UI Slider Example</h1>
      <VolumeSlider value={volume} onChange={setVolume} />
    </Container>
  );
}

ReactDOM.render(<App />, document.getElementById("root"));
