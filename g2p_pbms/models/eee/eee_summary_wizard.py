import logging
import requests

from odoo import models, fields, api
from odoo.tools.safe_eval import safe_eval

from ..registries import G2PRegistryType

_logger = logging.getLogger(__name__)

class G2PEEESummaryWizard(models.TransientModel):
    _name = 'g2p.eee.summary.wizard'
    _description = 'EEE Summary Wizard'
    _rec_name = 'mnemonic'

    target_registry_type = fields.Selection(
        selection=lambda self: G2PRegistryType.selection(),
        string="Registry Type",
        required=True,
    )
    mnemonic= fields.Char(string='Mnemonic')
    brief = fields.Text(string='Brief')
    program_id = fields.Many2one('g2p.program.definition', string='Program')
    beneficiary_list_id = fields.Integer(string='Beneficiary List ID')
    enrollment_cycle_id = fields.Integer(string='Enrollment Cycle')
    disbursement_cycle_id = fields.Integer(string='Disbursement Cycle')
    beneficiary_search = fields.Char(string='Search Beneficiary')
    list_stage = fields.Char(string='List Stage', default="enrollment")
    list_workflow_status = fields.Char(string='List Workflow Status', default="initiated")

    feedback_ids = fields.One2many(
        "g2p.beneficiary.list.feedback",
        string="Feedback",
        compute="_compute_feedback_ids",
        default=False
    )
    verification_ids = fields.One2many(
        "g2p.beneficiary.list.verification",
        string="Verification",
        compute="_compute_verification_ids",
        default=False
    )

    # Enrollment Cycle Info
    enrollment_start_date = fields.Date(string='Enrollment Start Date')
    enrollment_end_date = fields.Date(string='Enrollment End Date')

    # Disbursement Cycle Info
    disbursement_cycle_mnemonic = fields.Char(string='Disbursement Cycle')
    approved_for_disbursement = fields.Boolean(string='Approved for Disbursement', default=False)

    # Store all summary lines from the API response
    summary_line_ids = fields.One2many(
        'g2p.api.summary.line', 'wizard_id', string='Summary Details',
        compute='_compute_summary_lines', store=True
    )
    # Computed filtered fields (not stored) for UI display
    summary_general_line_ids = fields.One2many(
        'g2p.api.summary.line', 'wizard_id', string='General Info',
        compute='_compute_general'
    )
    summary_registry_line_ids = fields.One2many(
        'g2p.api.summary.line', 'wizard_id', string='Registry Info',
        compute='_compute_registry'
    )
    group_title = fields.Char(compute='_compute_group_title', string="Group Title")

    dummy_beneficiaries_field = fields.Text(string="Beneficiaries", compute="_compute_dummy")

    sql_query = fields.Char(string="Query", compute="_get_query", store=True)
    order_by_condition = fields.Char(string="Order By", default="name")

    def _compute_dummy(self):
        for wizard in self:
            wizard.dummy_beneficiaries_field = ""

    @api.depends('target_registry_type')
    def _compute_group_title(self):
        for rec in self:
            rec.group_title = 'Eligibility & Entitlement Statistics for %s' % rec.target_registry_type.capitalize()

    @api.depends("beneficiary_search", "target_registry_type")
    def _get_query(self):
        for rec in self:
            try:
                # Convert the domain string into a valid Python list of tuples.
                domain_value = safe_eval(rec.beneficiary_search or "[]")
            except Exception as e:
                _logger.error(
                    "Error evaluating domain: %s",
                    e,
                )
                rec.sql_query = "Invalid search term"
                continue

            # Define a mapping from the selection value to the target model.
            target_model_mapping = {
                "student": "g2p.student.registry",
                "farmer": "g2p.farmer.registry",
                # add additional mappings if needed
            }
            target_model_name = target_model_mapping.get(rec.target_registry_type)
            if not target_model_name:
                _logger.error(
                    "Unknown target_registry_type '%s'",
                    rec.target_registry_type,
                )
                rec.sql_query = "Unknown target registry type"
                continue
            
            order_by_field = "id"
            if rec.target_registry_type == "student":
                # Add a default order by field for the student registry.
                order_by_field = "name"
            elif rec.target_registry_type == "farmer":
                order_by_field = "name"
            

            # Get the target model's recordset.
            target_model = self.env[target_model_name]

            try:
                # Calculate the where clause for the target model based on the evaluated domain.
                query = target_model._where_calc(domain_value)
            except Exception as e:
                _logger.error(
                    "Error calculating where clause for rule %s: %s", rec.mnemonic, e
                )
                rec.sql_query = "Error calculating query"
                continue

            try:
                _, where_clause, where_clause_params = query.get_sql()
            except Exception as e:
                _logger.error(
                    "Error generating SQL from query: %s", e
                )
                rec.sql_query = "Error generating SQL"
                continue

            where_str = ("%s" % where_clause) if where_clause else ""
            # Use the target model's table name in the SQL query.
            query_str = (
                where_str 
            )
            
            # Format the parameters as strings.
            formatted_params = list(
                map(lambda x: "'" + str(x) + "'", where_clause_params)
            )

            try:
                formatted_query = query_str % tuple(formatted_params)
                # formatted_query = formatted_query.replace('"', '\\"')
                rec.sql_query = formatted_query
                rec.order_by_condition = order_by_field
                _logger.info("Query: %s", rec.sql_query)
            except Exception as e:
                _logger.error(
                    "Error formatting query: %s",
                    e,
                )
                rec.sql_query = "Error formatting query"

    @api.model
    def get_beneficiaries(self, wizard_id, page, page_size):
        wizard = self.browse(wizard_id)
        target_registry_type = wizard.target_registry_type
        api_url = self.env['ir.config_parameter'].sudo().get_param('g2p_pbms.eee_api_url')
        if not api_url:
            _logger.error("API URL not set in environment")
        endpoint = f"{api_url}/search_beneficiaries"
        payload = {
            "signature": "string",
                "header": {
                    "version": "1.0.0",
                    "message_id": "string",
                    "message_ts": "string",
                    "action": "search_beneficiaries",
                    "sender_id": "string",
                    "sender_uri": "",
                    "receiver_id": "",
                    "total_count": 0,
                    "is_msg_encrypted": False,
                    "meta": "string"
                },
            "message": {
                "beneficiary_list_id": wizard.beneficiary_list_id,
                "target_registry_type": target_registry_type,
                "page": page,
                "page_size": page_size,
                "search_query": wizard.sql_query or "",
                "order_by": wizard.order_by_condition or "id asc",
            }
        }
        try:
            response = requests.post(endpoint, json=payload, timeout=10)
            response.raise_for_status()
            api_response = response.json()
            _logger.info("API response: %s", api_response)
        except Exception as e:
            _logger.error("API call failed: %s", e)
            return {
                "message": {
                    "total_beneficiary_count": 0,
                    "page": page,
                    "page_size": page_size,
                    "beneficiaries": []
                }
            }
        return api_response


    @api.depends('target_registry_type', 'beneficiary_search')
    def _compute_summary_lines(self):
        excluded_keys = ['id', 'target_registry_type']
        for wizard in self:
            wizard.summary_line_ids = [(5, 0, 0)]
            api_url = self.env['ir.config_parameter'].sudo().get_param('g2p_pbms.eee_api_url')
            if not api_url:
                _logger.error("API_URL not set in environment")
            endpoint = f"{api_url}/eee_summary"
            payload = {
                "signature": "string",
                "header": {
                    "version": "1.0.0",
                    "message_id": "string",
                    "message_ts": "string",
                    "action": "eee_summary",
                    "sender_id": "string",
                    "sender_uri": "",
                    "receiver_id": "",
                    "total_count": 0,
                    "is_msg_encrypted": False,
                    "meta": "string"
                },
                "message": {
                    "beneficiary_list_id": wizard.beneficiary_list_id,
                    "target_registry_type": wizard.target_registry_type
                }
            }
            try:
                response = requests.post(endpoint, json=payload, timeout=10)
                response.raise_for_status()
                api_response = response.json()
                _logger.info("API response: %s", api_response)
            except Exception as e:
                _logger.error("API call failed: %s", e)
                _logger.info("API Endpoint: %s", endpoint)
                return {
                    "message": {
                        "general_summary": {},
                        "registry_summary": {}
                    }
                }
            lines = []
            message = api_response.get('message', {})

            # Process all keys from general_summary
            for key, value in message.get('general_summary', {}).items():
                if key in excluded_keys:
                    continue
                lines.append((0, 0, {
                    'wizard_id': wizard.id,
                    'key': key.replace('_', ' ').title(),
                    'value': str(int(value) if isinstance(value, float) else value),
                    # 'value': f"{value:.2f}" if isinstance(value, float) else str(value),
                    'summary_type': 'general'
                }))

            # Process all keys from registry_summary
            for key, value in message.get('registry_summary', {}).items():
                if key in excluded_keys:
                    continue
                lines.append((0, 0, {
                    'wizard_id': wizard.id,
                    'key': key.replace('_', ' ').title(),
                    'value': str(int(value) if isinstance(value, float) else value),
                    # 'value': f"{value:.2f}" if isinstance(value, float) else str(value),
                    'summary_type': 'registry'
                }))

            wizard.summary_line_ids = lines



    @api.depends('summary_line_ids')
    def _compute_general(self):
        for wizard in self:
            wizard.summary_general_line_ids = wizard.summary_line_ids.filtered(
                lambda r: r.summary_type == 'general'
            )

    @api.depends('summary_line_ids')
    def _compute_registry(self):
        for wizard in self:
            wizard.summary_registry_line_ids = wizard.summary_line_ids.filtered(
                lambda r: r.summary_type == 'registry'
            )
    
    @api.depends('beneficiary_list_id')
    def _compute_feedback_ids(self):
        for wizard in self:
            if wizard.beneficiary_list_id:
                wizard.feedback_ids = self.env['g2p.beneficiary.list.feedback'].search([
                    ('beneficiary_list_id.id', '=', wizard.beneficiary_list_id)
                ])
            else:
                wizard.feedback_ids = False

    @api.depends('beneficiary_list_id')
    def _compute_verification_ids(self):
        for wizard in self:
            if wizard.beneficiary_list_id:
                wizard.verification_ids = self.env['g2p.beneficiary.list.verification'].search([
                    ('beneficiary_list_id.id', '=', wizard.beneficiary_list_id)
                ])
            else:
                wizard.verification_ids = False

    def action_publish_to_communities(self):
        self.ensure_one()
        if not self.list_workflow_status == 'published_to_communities':
            self.list_workflow_status = 'published_to_communities'
            self.env['g2p.beneficiary.list'].browse(self.beneficiary_list_id).write({
                'list_workflow_status': 'published_to_communities'
            })
    
    def action_approve_final_enrollment(self):
        self.ensure_one()
        if not self.list_workflow_status == 'approved_final_enrolment':
            self.list_workflow_status = 'approved_final_enrolment'
            self.env['g2p.beneficiary.list'].browse(self.beneficiary_list_id).write({
                'list_workflow_status': 'approved_final_enrolment'
            })
    
    def action_record_community_feedbacks(self):
        self.ensure_one()
        # Implement the logic to record community feedbacks under
        return {
            'type': 'ir.actions.act_window',
            'name': 'Record Community Feedback',
            'res_model': 'g2p.beneficiary.list.feedback',
            'view_mode': 'form',
            'view_id': self.env.ref('g2p_pbms.view_g2p_beneficiary_list_feedback_form').id,
            'target': 'new',
            'context': {
                'default_beneficiary_list_id': self.beneficiary_list_id,
                'beneficiary_list_feedback_form_edit': True,
            },
        }
    
    def action_approve_for_disbursement(self):
        self.ensure_one()
        if not self.list_workflow_status == 'approved_for_disbursement':
            self.list_workflow_status = 'approved_for_disbursement'
            self.approved_for_disbursement = True
            self.env['g2p.beneficiary.list'].browse(self.beneficiary_list_id).write({
                'list_workflow_status': 'approved_for_disbursement',
                'disbursement_envelope_status': 'pending'
            })
            self.env['g2p.disbursement.cycle'].browse(self.disbursement_cycle_id).write({
                'approved_for_disbursement': True,
            })

class G2PAPISummaryLine(models.TransientModel):
    _name = 'g2p.api.summary.line'
    _description = 'Dynamic API Summary Line'

    wizard_id = fields.Many2one('g2p.eee.summary.wizard', string='Wizard')
    key = fields.Char(string='Field')
    value = fields.Text(string='Value')
    summary_type = fields.Selection(
        [('general', 'General'), ('registry', 'Registry')],
        string="Summary Type",
        default='general'
    )
