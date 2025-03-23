import React from 'react';
import { withStyles } from '@mui/styles';
import Switch from '@mui/material/Switch';
import FormControlLabel from '@mui/material/FormControlLabel';

const PowerSwitch = withStyles((theme) => ({
  switchBase: {
    color: theme.palette.error.main,
    '&$checked': {
      color: theme.palette.success.main,
    },
    '&$checked + $track': {
      backgroundColor: theme.palette.success.main,
    },
  },
  checked: {},
  track: {},
}))(Switch);

const PowerSwitchComponent = ({ checked, onChange, onToggle }) => {
  const handleChange = (event) => {
    onChange(event);
    onToggle(event.target.checked);
  };

  return (
    <FormControlLabel
      control={
        <PowerSwitch
          checked={checked}
          onChange={handleChange}
          name="powerSwitch"
        />
      }
      label="Power"
    />
  );
};

export default PowerSwitchComponent;