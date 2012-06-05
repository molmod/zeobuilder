# Iterative is a toolkit for iterative algorithms on a set of state variables.
# Copyright (C) 2007 - 2008 Toon Verstraelen <Toon.Verstraelen@UGent.be>
#
# This file is part of Iterative.
#
# Iterative is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 3
# of the License, or (at your option) any later version.
#
# Iterative is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, see <http://www.gnu.org/licenses/>
#
# --


__all__ = ["Status", "Algorithm"]


class Status(object):
    pass


class Algorithm(object):
    def __init__(self, root_expression, stop_criterion):
        self.root_expression = root_expression
        self.stop_criterion = stop_criterion

    def run(self, report):
        self.status = Status()
        self.status.step = 0
        self.status.state = self.root_expression.state

        self.initialize()
        while not self.iterate():
            self.status.step += 1
            report(self.status)
        self.status.step += 1
        report(self.status)

        self.finalize()

    def initialize(self):
        pass

    def iterate(self):
        raise NotImplementedError

    def finalize(self):
        pass





