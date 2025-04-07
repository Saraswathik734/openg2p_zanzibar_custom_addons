from odoo import models, fields, api
import logging

_logger = logging.getLogger(__name__)


class G2PDeliveryClassificationCodes(models.Model):
    _name = "g2p.delivery.classification.codes"
    _description = "Delivery Classification Codes"
    _table = "g2p_delivery_classification_codes"
    _rec_name = "delivery_classification_mnemonic"

    delivery_classification_mnemonic = fields.Char(
        string="Delivery Classification Mnemonic", required=True
    )
    description = fields.Char(string="Description")

    _sql_constraints = [
        (
            "unique_delivery_classification_mnemonic",
            "unique(delivery_classification_mnemonic)",
            "The delivery classification mnemonic must be unique!",
        )
    ]

    def action_open_edit(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'g2p.delivery.classification.codes',
            'res_id': self.id,
            'view_mode': 'form',
            'target': 'current',
            'context':{'create': False, 'delivery_classification_code_form_edit':True},
        }



