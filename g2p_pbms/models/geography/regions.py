from odoo import models, fields, api
import logging

_logger = logging.getLogger(__name__)


class G2PRegions(models.Model):
    _name = "g2p.regions"
    _description = "Regions Model"

    region_code = fields.Char(string="Region Code", required=True)
    region_name = fields.Char(string="Region Name", required=True)
