#!/usr/bin/env python2
# -*- Mode:Python; indent-tabs-mode:nil; tab-width:4 -*-
#
# Copyright 2002 Ben Escoto <ben@emerose.org>
# Copyright 2007 Kenneth Loafman <kenneth@loafman.com>
#
# This file is part of duplicity.
#
# Duplicity is free software; you can redistribute it and/or modify it
# under the terms of the GNU General Public License as published by the
# Free Software Foundation; either version 2 of the License, or (at your
# option) any later version.
#
# Duplicity is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with duplicity; if not, write to the Free Software Foundation,
# Inc., 59 Temple Place, Suite 330, Boston, MA 02111-1307 USA

import sys
import os
from setuptools import setup, Extension
from setuptools.command.test import test
from setuptools.command.install import install
from setuptools.command.sdist import sdist
from distutils.command.build_scripts import build_scripts

version_string = "0.1.0"

if sys.version_info[:2] < (2, 6) or sys.version_info[:2] > (2, 7):
    print("Sorry, duplicity-rclone requires version 2.6 or 2.7 of python.")
    sys.exit(1)

incdir_list = libdir_list = None

data_files = [ ('share/doc/duplicity-rclone-%s' % version_string,
               ['LICENSE',
                'README.md',]),
              ]

top_dir = os.path.dirname(os.path.abspath(__file__))

class InstallCommand(install):

    def run(self):
        # Normally, install will call build().  But we want to delete the
        # testing dir between building and installing.  So we manually build
        # and mark ourselves to skip building when we run() for real.
        self.run_command('build')
        self.skip_build = True

        # This should always be true, but just to make sure!
        if self.build_lib != top_dir:
            testing_dir = os.path.join(self.build_lib, 'testing')
            os.system("rm -rf %s" % testing_dir)

        install.run(self)

# don't touch my shebang
class BSCommand (build_scripts):

    def run(self):
        """
        Copy, chmod each script listed in 'self.scripts'
        essentially this is the stripped
         distutils.command.build_scripts.copy_scripts()
        routine
        """
        from stat import ST_MODE
        from distutils.dep_util import newer
        from distutils import log

        self.mkpath(self.build_dir)
        outfiles = []
        for script in self.scripts:
            outfile = os.path.join(self.build_dir, os.path.basename(script))
            outfiles.append(outfile)

            if not self.force and not newer(script, outfile):
                log.debug("not copying %s (up-to-date)", script)
                continue

            log.info("copying and NOT adjusting %s -> %s", script,
                     self.build_dir)
            self.copy_file(script, outfile)

        if os.name == 'posix':
            for file in outfiles:
                if self.dry_run:
                    log.info("changing mode of %s", file)
                else:
                    oldmode = os.stat(file)[ST_MODE] & 0o7777
                    newmode = (oldmode | 0o555) & 0o7777
                    if newmode != oldmode:
                        log.info("changing mode of %s from %o to %o",
                                 file, oldmode, newmode)
                        os.chmod(file, newmode)


setup(name="duplicity",
      version=version_string,
      description="duplicity backend for rclone",
      author=" GilGalaad",
      url="https://github.com/GilGalaad/duplicity-rclone",
      packages=['duplicity.backends',],
      package_dir={"duplicity.backends": "duplicity/backends", },
      data_files=data_files,
      cmdclass={
          'install': InstallCommand,
          'build_scripts': BSCommand,
      },
      )
