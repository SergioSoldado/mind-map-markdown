import * as React from 'react'
import Box from '@mui/material/Box'
import Slider from '@mui/material/Slider'

interface Props {
  onEvent: (value: number) => void
  maxSteps?: number
}

export default function ContinuousSlider({
  onEvent,
  maxSteps = undefined,
}: Props) {
  const [value, setValue] = React.useState<number>(2)
  const handleChange = (event: Event, newValue: number | number[]) => {
    setValue(newValue as number)
    onEvent(newValue as number)
  }

  if (maxSteps !== undefined) {
    return (
      <Box sx={{ width: 200 }}>
        <Slider
          aria-label="Depth"
          value={value}
          defaultValue={1}
          getAriaValueText={(value) => `${value} depth`}
          valueLabelDisplay={'auto'}
          onChange={handleChange}
          step={1}
          min={1}
          max={maxSteps}
          marks
        />
      </Box>
    )
  } else {
    return (
      <Box sx={{ width: 200 }}>
        <Slider aria-label="Depth" value={value} onChange={handleChange} />
      </Box>
    )
  }
}
