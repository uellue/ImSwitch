import importlib
import os
import traceback

from .imcommon import prepareApp, launchApp
from .imcommon.controller import ModuleCommunicationChannel, MultiModuleWindowController
from .imcommon.model import dirtools, modulesconfigtools
from .imcommon.view import MultiModuleWindow, ModuleLoadErrorView


def main():
    enabledModuleIds = modulesconfigtools.getEnabledModuleIds()
    if 'imscripting' in enabledModuleIds:
        # Ensure that imscripting is added last
        enabledModuleIds.append(enabledModuleIds.pop(enabledModuleIds.index('imscripting')))

    modulePkgs = [importlib.import_module(f'imswitch.{moduleId}')
                  for moduleId in modulesconfigtools.getEnabledModuleIds()]

    app = prepareApp()
    moduleCommChannel = ModuleCommunicationChannel()

    multiModuleWindow = MultiModuleWindow(
        'ImSwitch', os.path.join(dirtools.DataFileDirs.Root, 'icon.png')
    )
    multiModuleWindowController = MultiModuleWindowController.create(
        multiModuleWindow, moduleCommChannel
    )
    multiModuleWindow.show(showLoadingScreen=True)
    app.processEvents()  # Draw window before continuing

    # Register modules
    for modulePkg in modulePkgs:
        moduleCommChannel.register(modulePkg)

    # Load modules
    moduleMainControllers = dict()

    for i, modulePkg in enumerate(modulePkgs):
        moduleId = modulePkg.__name__
        moduleId = moduleId[moduleId.rindex('.')+1:]  # E.g. "imswitch.imcontrol" -> "imcontrol"

        # The displayed module name will be the module's __title__, or alternatively its ID if
        # __title__ is not set
        moduleName = modulePkg.__title__ if hasattr(modulePkg, '__title__') else moduleId

        try:
            view, controller = modulePkg.getMainViewAndController(
                moduleCommChannel=moduleCommChannel,
                multiModuleWindowController=multiModuleWindowController,
                moduleMainControllers=moduleMainControllers
            )
        except Exception as e:
            print(f'Failed to initialize module {moduleId}')
            print(traceback.format_exc())
            moduleCommChannel.unregister(modulePkg)
            multiModuleWindow.addModule(moduleId, moduleName, ModuleLoadErrorView(e))
        else:
            # Add module to window
            multiModuleWindow.addModule(moduleId, moduleName, view)
            moduleMainControllers[moduleId] = controller

            # Update loading progress
            multiModuleWindow.setLoadingProgress(i / len(modulePkgs))
            app.processEvents()  # Draw window before continuing

    launchApp(app, multiModuleWindow, moduleMainControllers.values())


if __name__ == '__main__':
    main()


# Copyright (C) 2020, 2021 TestaLab
# This file is part of ImSwitch.
#
# ImSwitch is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# ImSwitch is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.
