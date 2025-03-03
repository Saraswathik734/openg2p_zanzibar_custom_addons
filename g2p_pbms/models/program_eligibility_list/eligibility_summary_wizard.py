from odoo import models, fields, api
from ..registries import G2PRegistryType

class G2PEligibilitySummaryWizard(models.TransientModel):
    _name = 'g2p.eligibility.summary.wizard'
    _description = 'Eligibility Summary Wizard'
    _rec_name = 'brief'

    target_registry_type = fields.Selection(
        selection=lambda self: G2PRegistryType.selection(),
        string="Registry Type",
        required=True,
    )
    brief = fields.Text(string='Brief')
    program_id = fields.Many2one('g2p.program.definition', string='Program')
    beneficiary_search = fields.Char(string='Search Beneficiary')

    # Dynamic summary details from API (list of key/value pairs)
    summary_line_ids = fields.One2many(
        'g2p.api.summary.line', 'wizard_id', string='Summary Details', compute='_compute_summary_lines', store=True
    )
    # Dynamic beneficiaries returned from API
    eligibility_list_ids = fields.One2many(
        'g2p.api.beneficiary', 'wizard_id', string='Beneficiaries', compute='_compute_eligibility_list_ids',
    )

    @api.depends('target_registry_type')
    def _compute_summary_lines(self):
        for wizard in self:
            # Simulated API response based on registry type.
            if wizard.target_registry_type == 'farmer':
                api_response = {"Land Area": 150, "Cattle Heads": 12, "Poultry Heads": 30}
            elif wizard.target_registry_type == 'student':
                api_response = {"Institution": "Example University", "GPA": 3.7, "Credits": 120}
            else:
                api_response = {}
            # Assign command tuples instead of record objects.
            wizard.summary_line_ids = [(0, 0, {'key': key, 'value': str(value)}) for key, value in api_response.items()]

    @api.depends('beneficiary_search', 'target_registry_type')
    def _compute_eligibility_list_ids(self):
        for wizard in self:
            # Simulated API response for beneficiaries.
            api_response = [
                {'beneficiary_id': 'B001', 'name': 'Beneficiary One'},
                {'beneficiary_id': 'B002', 'name': 'Beneficiary Two'},
                {'beneficiary_id': 'B003', 'name': 'Other Beneficiary'},
            ]
            if wizard.beneficiary_search:
                term = wizard.beneficiary_search.lower()
                api_response = [rec for rec in api_response if term in rec.get('name', '').lower()]
            wizard.eligibility_list_ids = [
                (0, 0, {'beneficiary_id': rec.get('beneficiary_id'), 'name': rec.get('name')})
                for rec in api_response
            ]


class G2PAPISummaryLine(models.TransientModel):
    _name = 'g2p.api.summary.line'
    _description = 'Dynamic API Summary Line'

    wizard_id = fields.Many2one('g2p.eligibility.summary.wizard', string='Wizard')
    key = fields.Char(string='Field')
    value = fields.Text(string='Value')


class G2PAPIBeneficiary(models.TransientModel):
    _name = 'g2p.api.beneficiary'
    _description = 'Dynamic API Beneficiary'

    wizard_id = fields.Many2one('g2p.eligibility.summary.wizard', string='Wizard')
    beneficiary_id = fields.Char(string='Beneficiary ID')
    name = fields.Char(string='Name')