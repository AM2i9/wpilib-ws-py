# wpilib-ws-py
## An implementation of the WPILib WebSocket protocol for Python3

This library is an implementation of the WPILib simulation WebSocket, used for controlling non-frc hardware using WPILib. The specification of this protocol is found [here](https://github.com/wpilibsuite/allwpilib/blob/main/simulation/halsim_ws_core/doc/hardware_ws_api.md).

My own dive into the source code for the websocket, which has some undocumented information: https://github.com/AM2i9/wpilib-ws-py/payloads.md

[Example Sever Usage](https://github.com/AM2i9/wpilib-ws-py/tests/examples/demo_server.py):

```py
from wpilib_ws import WPILibWsServer

server = WPILibWsServer()

# The on_message decorator will let you create handlers for message events.
# Optionally a device type can be entered to only handle messages for that
# specific device type. A list of device types and other hardware messages can
# be found here:
# https://github.com/wpilibsuite/allwpilib/blob/main/simulation/halsim_ws_core/doc/hardware_ws_api.md#hardware-messages


@server.on_message("PWM")
async def pwm_handler(message):
    payload = message.data
    print(f"Recieved PWM event: {payload}")
    # ...


@server.on_message("CANMotor")
async def can_motor_handler(message):
    payload = message.data
    print(f"Recieved CANMotor event: {payload}")
    # ...


# Optionally, a device name can be entered to `on_message()`:


@server.on_message("SimDevice", "SPARK MAX")
async def spark_max_handler(message):

    # SimDevices are arbitrary devices sent over the websocket, which can be
    # used by vendor libraries to be able to use their controllers in robot
    # simulation. For example, SPARK MAX and other REV controllers will not
    # show as CAN devices, but as SimDevices.

    payload = message.data
    print(f"Recieved update for SPARK MAX controller: {payload}")


@server.on_message("CANMotor", "Victor SPX")
async def victor_handler(message):
    payload = message.data
    print(f"Recieved update for Victor SPX controller: {payload}")


# The while_connected decorator is a loop that runs alongside the server, and
# can be used for periodic tasks, such as sending battery voltage, like below.
@server.while_connected()
async def while_connected():
    await server.send_payload(
        {"type": "RoboRIO", "device": "", "data": {">vin_voltage": 12.0}}
    )


server.run()
```