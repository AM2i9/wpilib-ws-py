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
