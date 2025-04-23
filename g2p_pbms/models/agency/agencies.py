from odoo import models, fields, api
import logging

_logger = logging.getLogger(__name__)


class G2PAgencies(models.Model):
    _name = "g2p.agencies"
    _description = "Agencies Model"

    name = fields.Char(string="Name", required=True)
    mnemonic = fields.Char(string="Agency Mnemonic")
    benefit_codes = fields.Many2many("g2p.benefit.codes", string="Benefit Codes")
    regions = fields.Many2many("g2p.regions", string="Regions")

    def action_open_edit(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'g2p.agencies',
            'res_id': self.id,
            'view_mode': 'form',
            'target': 'current',
            'context':{'create': False, 'agency_form_edit':True},
        }

