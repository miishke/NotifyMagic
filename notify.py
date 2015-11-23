"""
Milos Miljkovic 2015

notify.py
version 1.0.0

IPython line and cell magic to notify user when kernel is done with execution.

Installation:

  %install_ext https://raw.githubusercontent.com/miishke/NotifyMagic/master/notify.py

Usage:

  %load_ext notify

Examples:

  import time

  Line magic
  %notify print('Test notify line magic')
  time.sleep(5)

  Cell magic
  %%notify
  time.sleep(5)
"""

import os
import platform
import subprocess
import json
from IPython.core.magic import magics_class, line_cell_magic
from IPython.core.magics.execution import ExecutionMagics
from IPython.core.magic_arguments import (argument, magic_arguments,
                                          parse_argstring)
from IPython.lib import kernel
from urllib.request import urlopen

@magics_class
class NotifyMagic(ExecutionMagics):
    """
    IPython line & cell magic notifying user when kernel is done with execution.
    """

    @magic_arguments()
    @argument('statement',  nargs='*', help='Code to run before notifying. You can omit this in cell magic mode.')
    @line_cell_magic
    def notify(self, line, cell=None):
        """
        IPython line & cell magic notifying user when kernel is done with execution.
        Example:
          import time
          # line magic
          %notify print('Test notify line magic')
          time.sleep(5)
          # cell magic
          %%notify
          time.sleep(5)
        """
        args = parse_argstring(self.notify, line)

        if cell:
            code = cell
        else:
            code = ' '.join(args.statement)

        self.shell.run_cell(code)

        connection_file_path = kernel.get_connection_file()
        connection_file = os.path.basename(connection_file_path)
        kernel_id = connection_file.split('-', 1)[1].split('.')[0]
        link = urlopen('http://127.0.0.1:8888/api/sessions')
        sessions = json.loads(link.read().decode('utf8'))
        for sess in sessions:
            if sess['kernel']['id'] == kernel_id:
                nb_relative_path = sess['notebook']['path']
                nb_name = os.path.basename(nb_relative_path)
                break

        platform_str = platform.system()
        if platform_str == 'Linux':
            cmd_str = 'notify-send "' +  'Kernel done' + '" "' + nb_name + '"'
        elif platform_str == 'Darwin':
            cmd_str = ('osascript -e \'display notification "' + nb_name +
                       '" with title "' + 'Kernel done' + '"\'')

        subprocess.call(cmd_str, shell=True)

def load_ipython_extension(ipython):
    ipython.register_magics(NotifyMagic)
