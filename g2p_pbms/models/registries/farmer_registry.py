from odoo import models, fields, api

from .registry import G2PRegistry


class G2PFarmerRegistry(models.Model):
    _name = "g2p.farmer.registry"
    _description = "Farmer Registry"
    _inherit = "g2p.registry"

    name = fields.Char(string="Name", required=True)
    land_area = fields.Float(string="Land Area")
    no_of_cattle_heads = fields.Integer(string="No of Cattle Heads")
    no_of_poultry_heads = fields.Integer(string="No of Poultry Heads")
