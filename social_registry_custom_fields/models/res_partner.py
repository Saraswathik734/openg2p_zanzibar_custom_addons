from odoo import models, fields

class ResPartner(models.Model):
    _inherit = "res.partner"

    benf_post_code = fields.Char(string="Post Code")
    benf_zan_id = fields.Char(string="Zan ID")
    disability = fields.Selection(
        [("yes", "Yes"), ("no", "No")], string="Do you have any disability?"
    )
    is_receiving_allowance = fields.Selection(
        [("yes", "Yes"), ("no", "No")],
        string="Are you receiving 5000 allowance from district council? (Below 70 years)",
    )
    has_health_insurance = fields.Selection(
        [("yes", "Yes"), ("no", "No")],
        string="Are you covered with any health insurance scheme?",
    )

    x_region_code=fields.Char("X_Reg")
    
    x_district_code=fields.Char("X_dist")
