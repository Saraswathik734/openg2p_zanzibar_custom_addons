from odoo import models, fields, api


class G2PRegistryType(models.Model):
    _name = "g2p.registry.type"
    _description = "Registry Type"

    mneumonic = fields.Char(string="Mneumonic", required=True)
    description = fields.Char(string="Description")
