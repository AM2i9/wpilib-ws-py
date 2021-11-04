from wpilib_ws import WPILibWsServer

server = WPILibWsServer()

# The on_message decorator will let you create handlers for message events.
# Optionally a device type can be entered to only handle messages for that
# specific device type. A list of device types and other hardware messages can
# be found here:
# https://github.com/wpilibsuite/allwpilib/blob/main/simulation/halsim_ws_core/doc/hardware_ws_api.md#hardware-messages


@server.on_message("PWM")
async def pwm_handler(event):
    payload = event.payload
    print(f"Recieved PWM event: {payload}")
    # ...


@server.on_message("CANMotor")
async def can_motor_handler(event):
    payload = event.payload
    print(f"Recieved CANMotor event: {payload}")
    # ...


# The while_connected decorator is a loop that runs alongside the server, and
# can be used for periodic tasks, such as sending battery voltage, like below.

@server.while_connected(buffer=0)
async def while_connected():
    await server.send_payload({
        "type": "RoboRIO",
        "device": "",
        "data": {">vin_voltage": 12.0}
    })


server.run()
