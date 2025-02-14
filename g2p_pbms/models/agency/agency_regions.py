from odoo import models, fields, api
import logging

_logger = logging.getLogger(__name__)


class G2PAgencyRegions(models.Model):
    _name = "g2p.agency.regions"
    _description = "Agency Regions Model"

    agency_id = fields.Many2one("g2p.agencies", string="Agency", required=True)
    region_id = fields.Integer(string="Region ID", required=True)
