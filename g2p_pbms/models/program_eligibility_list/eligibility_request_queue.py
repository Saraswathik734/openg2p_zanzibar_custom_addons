from odoo import models, fields, api


class G2PEligibilityRequestQueue(models.Model):
    _name = "g2p.eligibility.request.queue"
    _description = "G2P Eligibility Request Queue"

    program_id = fields.Many2one("g2p.program.definition", string="G2P Program")
    creation_date = fields.Datetime(string="Creation Date", default=fields.Datetime.now , readonly=True)
    brief = fields.Text(string="Brief")
    enumeration_status = fields.Selection(
        [
            ("pending", "PENDING"),
            ("complete", "COMPLETE"),
        ],
        string="Enumeration Status",
        default="pending",
    )
    processed_date = fields.Datetime(string="Processed Date", default=None, readonly=True)
