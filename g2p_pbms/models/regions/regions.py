from odoo import models, fields, api
import logging

_logger = logging.getLogger(__name__)


class G2PRegions(models.Model):
    _name = "g2p.regions"
    _description = "Regions Model"

    region_code = fields.Char(string="Region Code", required=True)
    region_name = fields.Char(string="Region Name", required=True)

    def action_open_edit(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'g2p.regions',
            'res_id': self.id,
            'view_mode': 'form',
            'target': 'current',
            'context':{'create': False, 'region_form_edit':True},
        }
