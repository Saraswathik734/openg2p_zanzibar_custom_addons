from odoo import models, fields, api
from ..registries import G2PRegistryType


class G2PProgramDefinition(models.Model):
    _name = "g2p.program.definition"
    _description = "G2P Program Definition"
    _table = "g2p_program_definition"
    _rec_name = "program_mnemonic"

    program_mnemonic = fields.Char(string="Program Mnemonic", required=True)
    description = fields.Char(string="Description")
    benefit_code_ids = fields.Many2many(
        'g2p.benefit.codes',
        string="Benefit Codes",
        required=True,
        help="Select benefit codes that are applicable for this program."
    )
    target_registry = fields.Selection(
        selection=G2PRegistryType.selection(), string="Target Registry", required=True
    )
    program_status = fields.Selection(
        [
            ("ACTIVE", "Active"),
            ("PAUSED", "Paused"),
            ("CLOSED", "Closed"),
        ],
        string="Program Status",
        required=True,
    )
    eligibility_rule_ids = fields.One2many(
        'g2p.eligibility.rule.definition', 'program_id', string="Eligibility Rules"
    )
    entitlement_rule_ids = fields.One2many(
        'g2p.entitlement.rule.definition', 'program_id', string="Entitlement Rules"
    )
    beneficiary_list_ids = fields.One2many(
        "g2p.beneficiary.list",
        "program_id",
        string="Eligibility Request Queue",
    )
    enrollment_cycle_ids = fields.One2many(
        "g2p.enrollment.cycle",
        "program_id",
        string="Enrollment Cycle",
    )
    disbursement_cycle_ids = fields.One2many(
        "g2p.disbursement.cycle",
        "program_id",
        string="Disbursement Cycle",
    )
    distribution_through_agencies = fields.Boolean(
        string="Distribution through Agencies",
        default=True,
        help="If checked, the program will require benefits to be collected from specified agencies. If unchecked, beneficiaries may collect benefits from any agency in the country. " \
    )
    only_direct_credit_allowed = fields.Boolean(
        string="Only Direct Credit Allowed",
        default=True,
        help="Cash will be directly credited to beneficiary accounts. Beneficiaries who don't have accounts will not receive benefits. Relevant only for cash benefits. " \
        "If Unchecked, benefits will be distributed as cash through agencies for beneficiaries without accounts."
    )

    #Entitlement Configuration
    # max_quantity = fields.Integer(string="Maximum Quantity")

    # Add related field for measurement_unit from benefit_id
    # measurement_unit = fields.Char(
    #     related='benefit_code_id.measurement_unit',
    #     string="Measurement Unit",
    #     readonly=True
    # )
    # benefit_type = fields.Selection(
    #     related='benefit_code_id.benefit_type',
    #     string="Benefit Type",
    #     readonly=True
    # )
    # display_quantity = fields.Char(string="Max Quantity", compute="_compute_display_quantity")

    # Cycle configuration
    disbursement_frequency = fields.Selection([
        ('Daily', 'Daily'),
        ('Weekly', 'Weekly'),
        ('Fortnightly', 'Fortnightly'),
        ('Monthly', 'Monthly'),
        ('BiMonthly', 'BiMonthly'),
        ('Quarterly', 'Quarterly'),
        ('SemiAnnually', 'SemiAnnually'),
        ('Annually', 'Annually'),
        ('OnDemand', 'OnDemand'),
    ], string="Disbursement Frequency", required=True, default='OnDemand')

    disbursement_day_of_week = fields.Selection([
        ('Monday', 'Monday'),
        ('Tuesday', 'Tuesday'),
        ('Wednesday', 'Wednesday'),
        ('Thursday', 'Thursday'),
        ('Friday', 'Friday'),
        ('Saturday', 'Saturday'),
        ('Sunday', 'Sunday'),
    ], string="Day of Week")

    disbursement_day_of_month = fields.Integer(string="Day of Month")
    disbursement_start_month = fields.Selection([
        ('January', 'January'),
        ('February', 'February'),
        ('March', 'March'),
        ('April', 'April'),
        ('May', 'May'),
        ('June', 'June'),
        ('July', 'July'),
        ('August', 'August'),
        ('September', 'September'),
        ('October', 'October'),
        ('November', 'November'),
        ('December', 'December'),
    ], string="Start Month")

    on_demand_cycle_allowed = fields.Boolean(string="On-Demand Cycle Allowed")

    beneficiary_list = fields.Selection([
        ('latest_always', 'Latest Always'),
        ('labeled', 'Labeled')
    ], string="Beneficiary List", required=True, default='latest_always')

    label_for_beneficiary_list_id = fields.Many2one(
        'g2p.beneficiary.list', 
        string="Label for Beneficiary List"
    )    
    # Computed booleans for dynamic visibility – stored to allow use in views.
    show_disbursement_day_of_week = fields.Boolean(compute='_compute_visibility_frequency', store=True)
    show_disbursement_day_of_month = fields.Boolean(compute='_compute_visibility_frequency', store=True)
    show_disbursement_start_month = fields.Boolean(compute='_compute_visibility_frequency', store=True)
    show_label_for_beneficiary_list = fields.Boolean(compute='_compute_visibility_beneficiary', store=True)

    _sql_constraints = [
        (
            "unique_program_mnemonic",
            "unique(program_mnemonic)",
            "The program mnemonic must be unique!",
        )
    ]

    @api.depends('disbursement_frequency')
    def _compute_visibility_frequency(self):
        for rec in self:
            rec.show_disbursement_day_of_week = rec.disbursement_frequency in ('Weekly')
            rec.show_disbursement_day_of_month = rec.disbursement_frequency in ('Fortnightly', 'BiMonthly', 'Monthly', 'Quarterly', 'SemiAnnually', 'Annually')
            rec.show_disbursement_start_month = rec.disbursement_frequency in ('Quarterly', 'SemiAnnually', 'Annually')
    
    @api.depends('beneficiary_list')
    def _compute_visibility_beneficiary(self):
        for rec in self:
            rec.show_label_for_beneficiary_list = rec.beneficiary_list == 'labeled'

    # @api.depends('max_quantity', 'measurement_unit')
    # def _compute_display_quantity(self):
    #     for rec in self:
    #         rec.display_quantity = f"{rec.max_quantity} {rec.measurement_unit or ''}"

    @api.depends('entitlement_id')
    def _compute_entitlement_inline_ids(self):
        for rec in self:
            rec.entitlement_inline_ids = rec.entitlement_id or False

    def action_open_edit(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'g2p.program.definition',
            'res_id': self.id,
            'view_mode': 'form',
            'target': 'current',
            'context':{'create': False, 'program_form_edit':True, 'program_form_create':False},
        }
