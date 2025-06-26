from odoo import models, fields, api
from datetime import date, timedelta

class G2PEnrollmentCycle(models.Model):
    _name = "g2p.enrollment.cycle"
    _description = "G2P Enrollment Cycle"
    _rec_name = "cycle_number"

    enrollment_cycle_id = fields.Char(string='Enrollment Cycle ID')
    cycle_number = fields.Integer(string="Cycle Number", required=True, default=lambda self: self._get_default_cycle_number())
    program_id = fields.Many2one("g2p.program.definition", string="G2P Program", readonly=True)
    beneficiary_list_ids = fields.One2many(
        "g2p.beneficiary.list", "enrollment_cycle_id", string="Beneficiary Lists"
    )
    enrollment_start_date = fields.Date(
        string="Enrollment Start Date", required=True, default=fields.Date.today
    )
    enrollment_end_date = fields.Date(
        string="Enrollment End Date", required=True, default=lambda self: date.today() + timedelta(days=30)
    )
    disbursement_start_date = fields.Date(
        string="Disbursement Start Date", required=True
    )
    disbursement_end_date = fields.Date(
        string="Disbursement End Date", required=True
    )
    is_readonly = fields.Boolean(compute='_compute_is_readonly', store=False)

    @api.depends_context('enrollment_cycle_form_view')
    def _compute_is_readonly(self):
        for rec in self:
            rec.is_readonly = self.env.context.get('enrollment_cycle_form_view', True)

    @api.model
    def _get_default_cycle_number(self):
        last = self.search([], order='cycle_number desc', limit=1)
        return last.cycle_number + 1 if last else 1

    def action_open_view(self):
        return {
            "type": "ir.actions.act_window",
            "name": "View Enrollment Cycle",
            "res_model": self._name,
            "res_id": self.id,
            "view_mode": "form",
            "target": "current",
            'context':{'create': False, 'enrollment_cycle_form_view':True},
        }
