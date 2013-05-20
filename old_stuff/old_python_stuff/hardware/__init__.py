import sys

if sys.platform.startswith("linux"):
    # linux systems
    from udev import *

elif sys.platform == "cygwin":
    # windows, maybe
    raise NotImplementedError(
        "Hardware detection in Voxelpress is not yet supported for your operating system.")

elif sys.platform == "darwin":
    # os x
    raise NotImplementedError(
        "Hardware detection in Voxelpress is not yet supported for your operating system.")

else:
    # no idea =)
    raise NotImplementedError(
        "Hardware detection in Voxelpress is not yet supported for your operating system.")
