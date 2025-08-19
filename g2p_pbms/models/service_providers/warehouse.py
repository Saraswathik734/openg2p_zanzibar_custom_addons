from odoo import models, fields, api
import logging

_logger = logging.getLogger(__name__)


class G2PWarehouse(models.Model):
    _name = "g2p.warehouse"
    _description = "Warehouse Model"
    _rec_name = "warehouse_mnemonic"

    name = fields.Char(string="Warehouse Name", required=True)
    warehouse_mnemonic = fields.Char(string="Warehouse Mnemonic")
    is_sponsor_bank = fields.Boolean(
        string="Is Sponsor Bank",
        help="Does this service provider operate as a sponsor bank?",
        default=False
    )
    admin_name = fields.Char(string="Admin Name")
    admin_email = fields.Char(string="Admin Email")
    admin_mobile = fields.Char(string="Admin Mobile")
    administrative_area_large_ids = fields.Many2many(
        "g2p.administrative.area.large",
        string="Administrative Areas (Large)"
    )
    warehouse_program_benefit_codes = fields.One2many(
        "g2p.warehouse.program.benefit.codes",
        "warehouse_id",
        string="Warehouse Program Benefit Codes"
    )

    def action_open_edit(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'g2p.agency',
            'res_id': self.id,
            'view_mode': 'form',
            'target': 'current',
            'context':{'create': False, 'agency_form_edit':True},
        }

