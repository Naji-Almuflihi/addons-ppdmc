# -*- coding: utf-8 -*-
##############################################################################
#
#    Global Creative Concepts Tech Co Ltd.
#    Copyright (C) 2018-TODAY iWesabe (<http://www.iwesabe.com>).
#    You can modify it under the terms of the GNU LESSER
#    GENERAL PUBLIC LICENSE (LGPL v3), Version 3.
#
#    It is forbidden to publish, distribute, sublicense, or sell copies
#    of the Software or modified copies of the Software.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU LESSER GENERAL PUBLIC LICENSE (LGPL v3) for more details.
#
#    You should have received a copy of the GNU LESSER GENERAL PUBLIC LICENSE
#    GENERAL PUBLIC LICENSE (LGPL v3) along with this program.
#    If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
import base64
from odoo import models, fields
from odoo.exceptions import UserError

default_code = """
def execute(self):
    pass
    """


class PythonExecute(models.TransientModel):
    _name = 'python.execute'

    code = fields.Text(default=default_code)
    py_file = fields.Binary(string='File')
    output = fields.Html(readonly=True)

    def execute_code(self):
        self.ensure_one()

        if not self.code.strip().startswith('def execute(self):'):
            raise UserError('Code should start with \'def execute(self):\'')

        try:

            lines = self.code.strip().split('\n')[1:]

            block = ""
            for line in lines:
                block += line[4:]
                block += '\n'
            print(block)
            exec(block)

        except Exception as e:
            raise UserError(str(e))

    def execute_file(self):
        self.ensure_one()

        if not self.py_file:
            raise UserError('Please upload Python Code !')

        content = base64.b64decode(self.py_file).decode("utf-8")

        if not content.strip().startswith('def execute(self):'):
            raise UserError('File should start with \'def execute(self):\'')

        lines = content.strip().split('\n')[1:]

        try:
            block = """
from odoo.exceptions import UserError
self.output = "Output :<br/><br/>"
def print(*vals, x=self):
    text = ''.join(map(str, vals))
    x.output += '<span style="font-weight:bold;">%s</span><br/>' % text
"""
            for line in lines:
                block += line[4:]
                block += '\n'

            exec(block)

            self.search([('id', '!=', self.id)]).unlink()  # CLEAN

        except Exception as e:
            raise UserError(str(e))





