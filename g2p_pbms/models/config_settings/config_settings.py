from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    g2p_pbms_eee_api_url = fields.Char(string="EEE API URL", config_parameter="g2p_pbms.eee_api_url")