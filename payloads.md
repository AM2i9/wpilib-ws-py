These are the device types and payloads sent and recieved by the WPILib Simulation. This is unofficial, and was found by looking through the source found [here](https://github.com/wpilibsuite/allwpilib/tree/main/simulation/halsim_ws_core/src/main/native/cpp).

---

### Addressable LEDs

Type name: `AddressableLED`

RGB data is also sent under the `"data"` key, looking to an array of RGB values 

Key | Type
--- | ---
`<init` | boolean
`<output_port` | int
`<length` | int
`<running` | boolean

### Analog In

Type name: `AI`

Key | Type
--- | ---
`<init` | boolean
`<avg_bits` | int
`<oversample_bits` | int
`>voltage` | double
`<accum_init` | bool
`>accum_value` | int
`>accum_count` | int
`<accum_center` | int
`<accum_deadband` | int

### Analog Out

Type name: `AO`

Key | Type
--- | ---
`<init` | bool
`<voltage` | double

### Accelerometer

Type name: `Accel`

Key | Type
--- | ---
`<init` | bool
`<range` | double
`>x` | double
`>y` | double
`>z` | double

### Digital I/O

Type name: `DIO`

Key | Type
--- | ---
`<init` | bool
`<>value` | bool
`<pulse_length` | double
`<input` | bool

### Driver Station

Type name: `DriverStation`

Key | Type
--- | ---
`>enabled` | bool
`>autonomous` | bool
`>test` | bool
`>estop` | bool
`>fms` | bool
`>ds` | bool
`>station` | string
`>match_time` | double
`>game_data` | string
`>new_data` | bool

### Encoder

Type name: `Encoder`

Key | Type
--- | ---
`<init` | bool
`<channel_a` | int
`<channel_b` | int
`>count` | int
`>period` | double
`<reverse_direction` | bool
`<samples_to_avg` | int

### Joystick

Type name: `Joystick`

Key | Type
--- | ---
`>axes` | Array[double]
`>povs` | Array[int]
`>buttons` | Array[bool]
`<outputs` | int
`<rumble_left` | int
`<rumble_right` | int

### PCM

Type name: `CTREPCM`

Key | Type
--- | ---
`<init` | bool
`>on` | bool
`<closed_loop` | bool
`>pressure_switch` | bool
`>current` | double

### Solenoid

Type name: `Solenoid`

Key | Type
--- | ---
`<init` | bool
`<output` | bool

### PWM

Type name: `PWM`

Key | Type
--- | ---
`<init` | bool
`<speed` | double
`<position` | double
`<raw` | int
`<period_scale` | int
`<zero_latch` | bool

### Relay

Type name: `Relay`

Key | Type
--- | ---
`<init_fwd` | bool
`<init_rev` | bool
`<fwd` | bool
`<rev` | bool

### RoboRIO

Type name: `RoboRIO`

Key | Type
--- | ---
`>fpga_button` | bool
`>vin_voltage` | double
`>vin_current` | double
`>6v_voltage` | double
`>6v_current` | double
`>6v_active` | bool
`>6v_faults` | int
`>5v_voltage` | double
`>5v_current` | double
`>5v_active` | bool
`>5v_faults` | int
`>3v_voltage` | double
`>3v_current` | double
`>3v_active` | bool
`>3v_faults` | int

### Digital PWM (dPWM)

Type name: `dPWM`

Key | Type
--- | ---
`<init` | bool
`<duty_cycle` | double
`<dio_pin` | int

### SimDevice

SimDevices have no specific keys, and are completely up to the robot code as to what to send. Things like vendor libraries can use this to send data for interfaces such as CAN.