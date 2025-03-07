import logging
import requests

from odoo import models, fields, api
from odoo.tools.safe_eval import safe_eval

from ..registries import G2PRegistryType

_logger = logging.getLogger(__name__)

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
        'g2p.api.beneficiary', 'wizard_id', string='Beneficiaries', compute='_compute_eligibility_list_ids', store=True
    )
    sql_query = fields.Char(string="Query", compute="_get_query", store=True)

    page = fields.Integer(string='Page', default=1)
    page_size = fields.Integer(string='Page Size', default=3)
    total_count = fields.Integer(string='Total Count', readonly=True)
    page_info = fields.Char(string='Page Info', compute='_compute_page_info')

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
                where_str + " order by %s asc" % order_by_field
            )

            # Format the parameters as strings.
            formatted_params = list(
                map(lambda x: "'" + str(x) + "'", where_clause_params)
            )

            try:
                rec.sql_query = query_str % tuple(formatted_params)
                _logger.info("Query: %s", rec.sql_query)
            except Exception as e:
                _logger.error(
                    "Error formatting query: %s",
                    e,
                )
                rec.sql_query = "Error formatting query"

    @api.depends('target_registry_type', 'beneficiary_search')
    def _compute_summary_lines(self):
        for wizard in self:
            # Clear previous records
            wizard.summary_line_ids = [(5, 0, 0)]
            
            if not wizard.target_registry_type:
                _logger.warning("No target_registry_type provided; skipping summary computation.")
                continue

            # Read API URL from system parameters
            api_url = self.env['ir.config_parameter'].sudo().get_param('API_URL')
            if not api_url:
                _logger.error("API_URL not set in environment")
                # continue

            endpoint = f"{api_url}/get_summary"
            try:
                response = requests.get(endpoint, params={'type': wizard.target_registry_type}, timeout=10)
                response.raise_for_status()
                api_response = response.json()
                _logger.info("API response: %s", api_response)
            except Exception as e:
                _logger.error("API call failed: %s", e)
                api_response = {
                    "message": {
                        "id": 2,
                        "program_id": 2,
                        "program_mnemonic": "P2",
                        "target_registry_type": "student",
                        "eligibility_request_id": 2,
                        "number_of_registrants": 3,
                        "date_created": "2025-02-28T12:24:00.562302",
                        "age_mean": 10.33,
                        "age_quartile_25": 8,
                        "age_quartile_50": 9,
                        "age_quartile_75": 12
                    }
                }

            # Build summary lines, including the linking field wizard_id
            lines = [
                (0, 0, {'wizard_id': wizard.id, 'key': key, 'value': str(value)})
                for key, value in api_response.get('message', {}).items()
            ]
            _logger.info("Summary lines: %s", lines)
            wizard.summary_line_ids = [(5, 0, 0)] + lines


    @api.depends('beneficiary_search', 'target_registry_type', 'page', 'page_size')
    def _compute_eligibility_list_ids(self):
        for wizard in self:
            # Simulated full API response for beneficiaries.
            all_beneficiaries = [
                {'beneficiary_id': 'B001', 'name': 'Beneficiary One'},
                {'beneficiary_id': 'B002', 'name': 'Beneficiary Two'},
                {'beneficiary_id': 'B003', 'name': 'Other Beneficiary'},
                {'beneficiary_id': 'B004', 'name': 'Beneficiary Four'},
                {'beneficiary_id': 'B005', 'name': 'Beneficiary Five'},
                {'beneficiary_id': 'B006', 'name': 'Beneficiary Six'},
                {'beneficiary_id': 'B007', 'name': 'Beneficiary Seven'},
                {'beneficiary_id': 'B008', 'name': 'Beneficiary Eight'},
                # Add more mock records as needed for pagination.
            ]
            # Apply search filter if provided.
            if wizard.beneficiary_search:
                term = wizard.beneficiary_search.lower()
                _logger.info("Search term: %s", term)
                all_beneficiaries = [
                    rec for rec in all_beneficiaries
                    if term in rec.get('name', '').lower()
                ]
            # Set total count for pagination.
            wizard.total_count = len(all_beneficiaries)
            # Use wizard.page and wizard.page_size to simulate pagination.
            page = wizard.page or 1
            page_size = wizard.page_size or 3
            start_index = (page - 1) * page_size
            end_index = start_index + page_size
            paged_response = all_beneficiaries[start_index:end_index]
            _logger.info("Paged response: %s", paged_response)
            # Update eligibility list with the paged data.
            wizard.eligibility_list_ids = [(5, 0, 0)] + [
                (0, 0, {'beneficiary_id': rec.get('beneficiary_id'), 'name': rec.get('name')})
                for rec in paged_response
            ]
            _logger.info("Eligibility list: %s", wizard.eligibility_list_ids)

    def previous_page(self):
        for wizard in self:
            wizard.page = max(1, wizard.page - 1)
            wizard._compute_eligibility_list_ids()
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'g2p.eligibility.summary.wizard',
            'view_mode': 'form',
            'res_id': self.id,
            'target': 'current',
        }


    def next_page(self):
        for wizard in self:
            total_pages = (wizard.total_count // wizard.page_size) + (wizard.total_count % wizard.page_size and 1 or 0)
            if wizard.page < total_pages:
                wizard.page += 1
                wizard._compute_eligibility_list_ids()
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'g2p.eligibility.summary.wizard',
            'view_mode': 'form',
            'res_id': self.id,
            'target': 'current',
        }
    
    @api.depends('page', 'page_size', 'total_count')
    def _compute_page_info(self):
        for wizard in self:
            if wizard.page_size:
                total_pages = (wizard.total_count // wizard.page_size) + (1 if wizard.total_count % wizard.page_size else 0)
            else:
                total_pages = 0
            wizard.page_info = f"{wizard.page}/{total_pages}" if total_pages > 0 else "0/0"



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