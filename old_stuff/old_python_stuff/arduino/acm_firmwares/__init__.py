

def select_firmware(connection):
    """Autodetects firmware and returns a Reprap object.
    Returns None if no match is found."""

    found = None

    if connection.motd.count("Sprinter"):
        from .sprinter import SprinterReprap
        found = SprinterReprap(connection)

    elif connection.motd.count("Marlin"):
        from .marlin import MarlinReprap
        found = MarlinReprap(connection)

    return found
