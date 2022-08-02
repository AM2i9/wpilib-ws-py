from enum import Enum

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
    PCM = "CTREPCM"
    PWM = "PWM"
    Relay = "Relay"
    Solenoid = "Solenoid"
    SimDevice = "SimDevice"
    RoboRIO = "RoboRIO"

    @classmethod
    def device_exists(cls, device_type):
        return device_type in cls._value2member_map_


class CANDeviceType(Enum):
    Motor = "CANMotor"
    Encoder = "CANEncoder"
    Gyro = "CANGyro"
    Accelerometer = "CANAccel"
    AnalogInput = "CANAIn"
    DigitalIO = "CANDIO"
    DutyCycle = "CANDutyCycle"

    @classmethod
    def device_exists(cls, device_type):
        return device_type in cls._value2member_map_
