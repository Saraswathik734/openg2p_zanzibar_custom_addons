from odoo import models, fields, api
import logging

_logger = logging.getLogger(__name__)


class G2PAgencies(models.Model):
    _name = "g2p.agencies"
    _description = "Agencies Model"

    name = fields.Char(string="Name", required=True)
    mnemonic = fields.Char(string="Agency Mnemonic")
    delivery_codes = fields.Many2many("g2p.delivery.codes", string="Delivery Codes")
    regions = fields.Many2many("g2p.regions", string="Regions")

    def action_open_edit(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Edit Record',
            'res_model': self._name,
            'res_id': self.id,
            'view_mode': 'form',
            'target': 'new',
            'flags': {'mode': 'edit'},
        }

    def action_open_view(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'View Record',
            'res_model': self._name,
            'res_id': self.id,
            'view_mode': 'form',
            'target': 'new',
            'flags': {'mode': 'readonly'}
        }


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
