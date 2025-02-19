from odoo import models, fields, api


class G2PEligibilitySummaryStudent(models.Model):
    _name = "g2p.eligibility.summary.student"
    _description = "Student Eligibility Summary"
    _inherit = "g2p.eligibility.summary"

    age_quartile_25 = fields.Float(string="Age Quartile 25")
    age_quartile_50 = fields.Float(string="Age Quartile 50")
    age_quartile_75 = fields.Float(string="Age Quartile 75")

    eligibility_list_ids = fields.One2many(
        "g2p.eligibility.list",
        "eligibility_summary_student_id",
        string="Eligibility List",
    )
