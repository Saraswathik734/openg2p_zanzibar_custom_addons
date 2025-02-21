from odoo import models, fields, api


class G2PEligibilitySummaryFarmer(models.Model):
    _name = "g2p.eligibility.summary.farmer"
    _description = "Farmer Eligibility Summary"
    _inherit = "g2p.eligibility.summary"

    land_quartile_25 = fields.Float(string="Land Quartile 25")
    land_quartile_50 = fields.Float(string="Land Quartile 50")
    land_quartile_75 = fields.Float(string="Land Quartile 75")

    eligibility_list_ids = fields.One2many(
        "g2p.eligibility.list",
        "eligibility_summary_farmer_id",
        string="Eligibility List",
    )
