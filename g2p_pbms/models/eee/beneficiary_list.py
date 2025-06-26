import uuid
from odoo import models, fields, api


class G2PBeneficiaryList(models.Model):
    _name = "g2p.beneficiary.list"
    _description = "G2P Beneficiary List"
    _rec_name = "brief"

    beneficiary_list_id = fields.Char(string='Beneficiary List ID', readonly=True, required=True, default=lambda self: str(uuid.uuid4()))
    mnemonic = fields.Char(string="Mnemonic", required=True)
    program_id = fields.Many2one("g2p.program.definition", string="G2P Program", compute="_compute_program_id", store=True, readonly=True)
    enrollment_cycle_id = fields.Many2one("g2p.enrollment.cycle", string="Enrollment Cycle", nullable=True)
    disbursement_cycle_id = fields.Many2one("g2p.disbursement.cycle", string="Disbursement Cycle", nullable=True)

    brief = fields.Text(string="Brief")
    eligibility_process_status = fields.Selection(
        [
            ("not_applicable", "NOT APPLICABLE"),
            ("pending", "PENDING"),
            ("processing", "PROCESSING"),
            ("complete", "COMPLETE"),
        ],
        string="Eligibility Process Status",
        default="pending",
    )
    entitlement_process_status = fields.Selection(
        [
            ("not_applicable", "NOT APPLICABLE"),
            ("pending", "PENDING"),
            ("processing", "PROCESSING"),
            ("complete", "COMPLETE"),
        ],
        string="Entitlement Process Status",
        default="not_applicable",
    )
    disbursement_envelope_status = fields.Selection(
        [
            ("not_applicable", "NOT APPLICABLE"),
            ("pending", "PENDING"),
            ("processing", "PROCESSING"),
            ("complete", "COMPLETE"),
        ],
        string="Disbursement Envelope Status",
        default="not_applicable",
    )
    disbursement_batch_creation_status = fields.Selection(
        [
            ("not_applicable", "NOT APPLICABLE"),
            ("pending", "PENDING"),
            ("processing", "PROCESSING"),
            ("complete", "COMPLETE"),
        ],
        string="Disbursement Envelope Status",
        default="not_applicable",
    )
    list_stage = fields.Selection(
        [
            ("enrollment", "ENROLLMENT"),
            ("disbursement", "DISBURSEMENT")
        ],
        string="List Stage",
    )
    list_workflow_status = fields.Selection(
        [
            ("initiated", "INITIATED"),
            ("published_to_communities", "PUBLISHED TO COMMUNITIES"),
            ("approved_final_enrolment", "APPROVED FINAL ENROLMENT"), # TODO: approved_for_final_enrollment
            ("approved_for_disbursement", "APPROVED FOR DISBURSEMENT"),
        ],
        string="List Workflow Status",
        default="initiated",
    )
    feedback_ids = fields.One2many(
        "g2p.beneficiary.list.feedback",
        "beneficiary_list_id",
        string="Feedback",
    )
    verification_ids = fields.One2many(
        "g2p.beneficiary.list.verification",
        "beneficiary_list_id",
        string="Verification",
    )
    creation_date = fields.Datetime(string="Creation Date", default=fields.Datetime.now , readonly=True)
    processed_date = fields.Datetime(string="Processed Date", default=None, readonly=True)
    
    @api.depends('enrollment_cycle_id.program_id', 'disbursement_cycle_id.program_id')
    def _compute_program_id(self):
        for record in self:
            if record.enrollment_cycle_id:
                record.program_id = record.enrollment_cycle_id.program_id
                record.list_stage = "enrollment"
            elif record.disbursement_cycle_id:
                record.program_id = record.disbursement_cycle_id.program_id
                record.list_stage = "disbursement"

    def action_open_summary_wizard(self):
        self.ensure_one()
        wizard_vals = {
            "target_registry_type": self.program_id.target_registry_type,
            "mnemonic": self.mnemonic,
            "brief": self.brief,
            "program_id": self.program_id.id,
            "beneficiary_list_id": self.id,
            "enrollment_cycle_id": self.enrollment_cycle_id,
            "disbursement_cycle_id": self.disbursement_cycle_id,
            "list_stage": self.list_stage,
            "list_workflow_status": self.list_workflow_status,
            "enrollment_start_date": self.enrollment_cycle_id.enrollment_start_date if self.enrollment_cycle_id else None,
            "enrollment_end_date": self.enrollment_cycle_id.enrollment_end_date if self.enrollment_cycle_id else None,
            "disbursement_cycle_mnemonic": self.disbursement_cycle_id.cycle_mnemonic if self.disbursement_cycle_id else None,
            "approved_for_disbursement": self.disbursement_cycle_id.approved_for_disbursement if self.disbursement_cycle_id else None,
        }

        wizard = self.env["g2p.eee.summary.wizard"].create(wizard_vals)
        return {
            "name": "Eligibility Summary Details",
            "view_mode": "form",
            "res_model": "g2p.eee.summary.wizard",
            "res_id": wizard.id,
            "type": "ir.actions.act_window",
            "target": "current",
            'context': {
                'default_target_registry_type': self.program_id.target_registry_type,
                'default_program_id': self.program_id.id,
                'default_beneficiary_list_id': self.beneficiary_list_id,
            },
        }
