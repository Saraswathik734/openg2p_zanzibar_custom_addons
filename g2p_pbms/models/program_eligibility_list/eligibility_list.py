from odoo import models, fields, api


class G2PEligibilityList(models.Model):
    _name = "g2p.eligibility.list"
    _description = "G2P Eligibility List"

    eligibility_request_id = fields.Many2one(
        "g2p.que.eee.request", string="Eligibility Request ID"
    )
    beneficiary_id = fields.Reference(
        selection=[
            ("g2p.farmer.registry", "Farmer Registry"),
            ("g2p.student.registry", "Student Registry"),
        ],
        string="Beneficiary ID",
    )
    eligibility_summary_farmer_id = fields.Many2one(
        "g2p.eligibility.summary.farmer", string="Farmer Eligibility Summary"
    )
    eligibility_summary_student_id = fields.Many2one(
        "g2p.eligibility.summary.student", string="Student Eligibility Summary"
    )
