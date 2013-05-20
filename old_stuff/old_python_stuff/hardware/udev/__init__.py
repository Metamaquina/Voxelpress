import gudev
from .. import serial_device


__UDEV_CLIENT = gudev.Client(["tty", "usb/usb_device"])
__ATTACHED = False
def CONNECT_HW_EVENTS(voxelpress):
    global __ATTACHED

    if not __ATTACHED:
        __UDEV_CLIENT.connect(
            "uevent", __create_callback(voxelpress), None)
        __ATTACHED = True
        __discover_hardware(voxelpress)


def SCAN_HW(voxelpress):
    for device in __UDEV_CLIENT.query_by_subsystem("tty"):
        hw_info = device.get_property("ID_SERIAL")
        if hw_info:
            try:
                usb_path = device.get_parent().get_parent().get_device_file()
                tty_path = device.get_device_file()
            except:
                # FIXME
                continue

            print "attempting to connect..."
            printer = serial_device.SerialDevice(usb_path, hw_info)
            if printer.on_connect(tty_path):
                voxelpress.hw_connect_event(printer)


def __create_callback(voxelpress):
    def callback(client, action, device, user_data):
        hw_info = device.get_property("ID_SERIAL")
        subsystem = device.get_subsystem()

        if action == "add" and subsystem == "tty":
            usb_path = device.get_parent().get_parent().get_device_file()
            tty_path = device.get_device_file()

            print "attempting to connect..."
            printer = serial_device.SerialDevice(usb_path, hw_info)
            if printer.on_connect(tty_path):
                voxelpress.hw_connect_event(printer)
                
        elif action == "remove" and subsystem == "usb":
            usb_path = device.get_device_file()
            voxelpress.hw_disconnect_event(usb_path)

    return callback


def __discover_hardware(voxelpress):
    pass
