from enum import Enum
from typing import List, Optional


# Device type enums
class DeviceType(Enum):
    Accelerometer = "Accel"
    AddressableLED = "AddressableLED"
    AnalogInput = "AI"
    AnalogOutput = "AO"
    DigitalIO = "DIO"
    DutyCycleOut = "dPWM"
    DriverStation = "DriverStation"
    DutyCycleInput = "DutyCycle"
    Encoder = "Encoder"
    Gyro = "Gyro"
    Joystick = "Joystick"
    PCM = "PCM"
    PWM = "PWM"
    Relay = "Relay"
    Solenoid = "Solenoid"
    SimDevice = "SimDevice"
    RoboRIO = "RoboRIO"


class CANDeviceType(Enum):
    Motor = "CANMotor"
    Encoder = "CANEncoder"
    Gyro = "CANGyro"
    Accelerometer = "CANAccel"
    AnalogInput = "CANAIn"
    DigitalIO = "CANDIO"
    DutyCycle = "CANDutyCycle"


# Device message payloads

class AccelerometerPayload:
    init: Optional[bool]
    range: Optional[float]
    x: Optional[float]
    y: Optional[float]
    z: Optional[float]

class AddressableLEDPayload:
    init: Optional[bool]

class AnalogInputPayload:
    init: Optional[bool]
    volatge: Optional[float]

class AnalogOutputPayload:
    init: Optional[bool]

class DigitalIOPayload:
    init: Optional[bool]
    duty_cycle: Optional[float]
    dio_pin: Optional[int]

class DutyCycleOutPayload:
    init: Optional[bool]
    duty_cycle: Optional[float]
    dio_pin: Optional[int]

class DriverStationPayload:
    new_data: Optional[bool]
    enabled: Optional[bool]
    autonomous: Optional[bool]
    test: Optional[bool]
    estop: Optional[bool]
    fms: Optional[bool]
    ds: Optional[bool]
    station: Optional[int]
    match_time: Optional[float]
    game_data: Optional[str]

class DutyCycleInputPayload:
    init: Optional[bool]
    connected: Optional[bool]
    position: Optional[float]

class EncoderPayload:
    init: Optional[bool]
    channel_a: Optional[int]
    channel_b: Optional[int]
    samples_to_avg: Optional[int]
    count: Optional[int]
    period: Optional[float]

class GyroPayload:
    init: Optional[bool]
    range: Optional[float]
    connected: Optional[bool]
    angle_x: Optional[float]
    angle_y: Optional[float]
    angle_z: Optional[float]
    rate_x: Optional[float]
    rate_y: Optional[float]
    rate_z: Optional[float]

class JoystickPayload:
    axes: Optional[List[float]]
    povs: Optional[List[int]]
    buttons: Optional[List[bool]]
    rumble_left: Optional[float]
    rumble_right: Optional[float]

class PCMPayload:
    pass

class PWMPayload:
    init: Optional[bool]
    speed: Optional[float]
    position: Optional[float]

class RelayPayload:
    init_fwd: Optional[bool]
    init_rev: Optional[bool]
    fwd: Optional[bool]
    rev: Optional[bool]

class SolenoidPayload:
    init = Optional[bool]
    output = Optional[bool]

class SimDevicePayload:
    pass

class RoboRIOPayload:
    pass
