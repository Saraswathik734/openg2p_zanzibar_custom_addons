from odoo import fields, models, api
from urllib.parse import urlparse


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    g2p_pbms_eee_api_url = fields.Char(string="EEE API URL", config_parameter="g2p_pbms.eee_api_url")
    g2p_bridge_api_url = fields.Char(string="G2P Bridge API URL", config_parameter="g2p_pbms.g2p_bridge_api_url")

    g2p_document_store = fields.Many2one(
        "storage.backend",
        string="G2P Documents Store",
        config_parameter="g2p_pbms.document_store",
    )