'''
    Show what copy of a particular piece of software is installed on your
    Windows nodes in the 'Extra Info 0' column.
'''

from System.Diagnostics import *
from System.IO import *
from System import TimeSpan

from Deadline.Events import *
from Deadline.Scripting import *

import _winreg


def GetDeadlineEventListener():
    return ConfigSlaveEventListener()


def CleanupDeadlineEventListener(eventListener):
    eventListener.Cleanup()


class ConfigSlaveEventListener (DeadlineEventListener):
    def __init__(self):
        self.OnSlaveStartedCallback += self.OnSlaveStarted

    def Cleanup(self):
        del self.OnSlaveStartedCallback

    # This is called every time the Slave starts
    def OnSlaveStarted(self, slavename):
        title = self.GetConfigEntry("Software Title")
    
        slave = RepositoryUtils.GetSlaveSettings(slavename, True)
        slave.SlaveExtraInfo0 = self.GetVersion(title)
        RepositoryUtils.SaveSlaveSettings(slave)

    def GetVersion(self, software_title):
        try:
            i = 0
            explorer = _winreg.OpenKey(
                _winreg.HKEY_LOCAL_MACHINE,
                'SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Uninstall'
            )

            while True:
                key = _winreg.EnumKey(explorer, i)
                if software_title in key:
                    print('Found "{0}" in the list of installed software'.format(key))
                
                    item = _winreg.OpenKey(explorer, key)
                    version, type = _winreg.QueryValueEx(item, 'DisplayVersion')
                    print(' It\'s version was {0}'.format(version))
                    _winreg.CloseKey(item)

                    _winreg.CloseKey(explorer)
                    return version
                i += 1

        except WindowsError as e:
            print(e)

        _winreg.CloseKey(explorer)

        return "unknown"
