# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models


class AdhInfoPasarActivity(models.Model):
    _name = 'adhimix.pre.info.pasar.activity'
    _description = 'Info Pasar Activity'
    _inherits = {'mail.message.subtype': 'subtype_id'}
    _rec_name = 'name'
    _order = "sequence"

    days = fields.Integer('Number of days', default=0,
                          help='Number of days before executing the action, allowing you to plan the date of the action.')
    sequence = fields.Integer('Sequence', default=0)
    # team_id = fields.Many2one('crm.team', string='Sales Team')
    subtype_id = fields.Many2one('mail.message.subtype', string='Message Subtype', required=True, ondelete='cascade')
    recommended_activity_ids = fields.Many2many(
        'adhimix.pre.info.pasar.activity', 'info_pasar_activity_rel', 'activity_id', 'recommended_id',
        string='Recommended Next Activities')
    preceding_activity_ids = fields.Many2many(
        'adhimix.pre.info.pasar.activity', 'info_pasar_activity_rel', 'recommended_id', 'activity_id',
        string='Preceding Activities')

    # setting a default value on inherited fields is a bit involved
    res_model = fields.Char('Model', related='subtype_id.res_model',)
    internal = fields.Boolean('Internal Only', related='subtype_id.internal', inherited=True, default=True)
    default = fields.Boolean('Default', related='subtype_id.default', inherited=True, default=False)

    @api.multi
    def unlink(self):
        activities = self.search([('subtype_id', '=', self.subtype_id.id)])
        # to ensure that the subtype is only linked the current activity
        if len(activities) == 1:
            self.subtype_id.unlink()
        return super(CrmActivity, self).unlink()
