from odoo import models, fields, api
import logging

_logger = logging.getLogger(__name__)


class G2PAgencies(models.Model):
    _name = "g2p.agencies"
    _description = "Agencies Model"

    name = fields.Char(string="Name", required=True)
    mnemonic = fields.Text(string="Agency Mnemonic")
    delivery_codes = fields.One2many("g2p.agency.delivery.codes", "agency_id", "Delivery Codes")
    region_ids = fields.One2many("g2p.agency.regions", "agency_id","Regions")


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
    delivery_description = fields.Char(string="Delivery Description")

    _sql_constraints = [
        (
            "unique_delivery_mnemonic",
            "unique(delivery_mnemonic)",
            "The delivery mnemonic must be unique!",
        )
    ]


class G2PAgencyDeliveryCodes(models.Model):
    _name = "g2p.agency.delivery.codes"
    _description = "Agency Delivery Codes"
    _table = "g2p_agency_delivery_codes"

    agency_id = fields.Many2one("g2p.agencies", string="Agency", required=True)
    delivery_id = fields.Many2one(
        "g2p.delivery.codes", string="Delivery Code", required=True
    )
