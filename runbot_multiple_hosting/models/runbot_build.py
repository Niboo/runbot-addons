# -*- encoding: utf-8 -*-
##############################################################################
#
#    Odoo, Open Source Management Solution
#    This module copyright (C) 2010 - 2014 Savoir-faire Linux
#    (<http://www.savoirfairelinux.com>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
import os
import glob
import shutil

from openerp import models, api, fields

from openerp.addons.runbot import runbot

import logging

_logger = logging.getLogger(__name__)
_logger.setLevel(logging.DEBUG)


class RunbotBuild(models.Model):
    _inherit = "runbot.build"

    @api.multi
    def checkout(self):
        result = super(RunbotBuild, self).checkout()
        for build in self:
            for extra_repo in build.repo_id.dependency_nested_ids:
                extra_repo.repository_id.git_export(extra_repo.reference, build.path())

            modules_to_move = [
                os.path.dirname(module)
                for module in glob.glob(build.path('*/__openerp__.py'))
            ]

            for module in runbot.uniq_list(modules_to_move):
                basename = os.path.basename(module)
                if os.path.exists(build.server('addons', basename)):
                    build._log(
                        'Building environment',
                        'You have duplicate modules in your branches "%s"' % basename
                    )
                    shutil.rmtree(build.server('addons', basename))
                shutil.move(module, build.server('addons'))

        return result

    @api.multi
    def github_status(self):
        """
        By default, we disable this feature.
        This method should be call only for github repo
        :return:
        """
        return