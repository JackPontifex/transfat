"""Contains functions useful for fatsorting drives."""

import os
import subprocess
import sys  # ONLY FOR ERROR OUTPUT


def fatsortAvailable():
    """Return true if fatsort is available and false otherwise.

    Checks if fatsort is available to the user.

    Returns:
        A boolean signaling whether fatsort is available.
    """
    fatCheck = subprocess.Popen(["bash", "-c", "type fatsort"],
                                stdout=subprocess.DEVNULL,
                                stderr=subprocess.DEVNULL)
    exitCode = fatCheck.wait()
    return bool(exitCode)


def findDeviceLocations(destinationPath, noninteractive=False, verbose=False,
                        quiet=False):
    """Return device and mount locations of a FAT drive.

    Find device and mount locations of the FAT device corresponding to
    the supplied destination path. If these locations can't be found
    automatically, find them interactively. If all of this fails, return
    a 2-tuple of empty strings.

    Args:
        destinationPath: A string containing a path somewhere on the
            mounted device.
        noninteractive: An optional boolean toggling whether to omit
            interactively finding device and mount locations if doing so
            automatically fails.
        verbose: An optional boolean toggling whether to give extra
            output.
        quiet: An optional boolean toggling whether to omit error
            output.

    Returns:
        A 2-tuple containing device location and mount location strings;
        or, if these locations can't be found, a 2-tuple of empty
        strings.
    """
    # Make sure destination is an absolute path
    destination = os.path.abspath(destinationPath)

    # Get list of FAT devices
    bashListCmd = "mount -t vfat | cut -f 1,3 -d ' '"
    deviceListProcess = subprocess.Popen(["bash", "-c", bashListCmd],
                                         stdout=subprocess.PIPE)

    # Read the devices list from Popen
    deviceString = deviceListProcess.communicate()[0].decode('ascii')
    deviceString = deviceString.rstrip()

    # Check if any FAT devices were found
    if deviceString == '':
        # No FAT devices found, return empty string
        return ('', '')

    # Split deviceString so we get a separate string for each device
    deviceList = deviceString.split('\n')

    # For each device, split into device location and mount location.
    # So in deviceListSep, deviceListSep[i][0] gives the device location
    # and deviceListSep[i][1] gives the mount location of the ith device
    deviceListSep = [deviceList[i].split() for i in range(len(deviceList))]

    # Test if destination path matches any mount locations
    for i in range(len(deviceList)):
        deviceLoc = deviceListSep[i][0]
        mountLoc = deviceListSep[i][1]

        if destination.startswith(mountLoc):
            # Found a match! Return device and mount location
            return (deviceLoc, mountLoc)

    # Something went wrong with the automation: if not set to
    # non-interactive mode, ask user if any of the FAT devices found
    # earlier match the intended destination; otherwise, just return
    # empty strings
    if not noninteractive:
        # Enumerate each device
        deviceListEnum = ["[%d] %s" % (i, deviceList[i-1])
                          for i in range(1, len(deviceList)+1)]

        # Add option to abort
        deviceListEnum.insert(0, "[0] abort!")

        # Prompt user for which device to use
        if verbose:
            print("Failed to find device automatically!")
        print("Mounted FAT devices:", end='\n\n')
        print(*deviceListEnum, sep='\n', end='\n\n')

        ans = int(
                input("Drive to transfer to or abort [0-%d]: "
                      % (len(deviceListEnum)-1))
                 )

        # Return appropriate device and mount strings
        if ans == 0:
            # User selected abort, so return empty strings
            return ('', '')
        elif ans > len(deviceListEnum)-1:
            if not quiet:
                print("ERROR: invalid index", file=sys.stderr)
            return ('', '')
        else:
            # Return requested device and mount location strings
            return (deviceListSep[ans-1][0], deviceListSep[ans-1][1])
    else:
        # Non-interactive mode is on, just return empty strings
        return ('', '')


def unmount(deviceLocation, verbose=False):
    """Unmount a device and return an exit code."""
    noiseLevel = []
    if verbose:
        noiseLevel += ['-v']

    exitCode = subprocess.Popen(['sudo', 'umount', deviceLocation]
                                + noiseLevel).wait()
    return exitCode


def mount(deviceLocation, verbose=False):
    """Mount a device and return an exit code."""
    noiseLevel = []
    if verbose:
        noiseLevel += ['-v']

    exitCode = subprocess.Popen(['sudo', 'mount', deviceLocation]
                                + noiseLevel).wait()
    return exitCode


def fatsort(deviceLocation, verbose=False):
    """fatsort a device and return an exit code."""
    noiseLevel = []
    if not verbose:
        noiseLevel += ['-q']

    exitCode = subprocess.Popen(['sudo', 'fatsort', deviceLocation]
                                + noiseLevel).wait()
    return exitCode