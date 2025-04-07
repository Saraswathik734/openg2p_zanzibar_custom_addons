from odoo import models, fields, api
import logging

_logger = logging.getLogger(__name__)


class G2PDeliveryCodes(models.Model):
    _name = "g2p.delivery.codes"
    _description = "Delivery Codes"
    _table = "g2p_delivery_codes"
    _rec_name = "delivery_mnemonic"

    delivery_mnemonic = fields.Char(string="Delivery Mnemonic", required=True)
    delivery_type = fields.Selection(
        [
            ("COMMODITY", "Commodity"),
            ("SERVICE", "Service"),
            ("COMBINATION", "Combination"),
        ],
        string="Delivery Type",
        required=True,
    )
    delivery_classification_id = fields.Many2one(
        "g2p.delivery.classification.codes",
        string="Delivery Classification",
        required=True,
    )
    delivery_description = fields.Text(string="Delivery Description")
    measurement_unit = fields.Char(string="Measurement Unit")

    _sql_constraints = [
        (
            "unique_delivery_mnemonic",
            "unique(delivery_mnemonic)",
            "The delivery mnemonic must be unique!",
        )
    ]

    def action_open_edit(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'g2p.delivery.codes',
            'res_id': self.id,
            'view_mode': 'form',
            'target': 'current',
            'context':{'create': False, 'delivery_code_form_edit':True},
        }

