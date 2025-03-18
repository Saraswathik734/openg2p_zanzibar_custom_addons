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
    summary_statistics_line_ids = fields.One2many(
        'g2p.api.summary.line', 'wizard_id', string='Statistics',
        compute='_compute_statistics'
    )

    dummy_beneficiaries_field = fields.Text(string="Beneficiaries", compute="_compute_dummy")

    sql_query = fields.Char(string="Query", compute="_get_query", store=True)
    order_by_condition = fields.Char(string="Order By", default="name")
    
    page = fields.Integer(string='Page', default=1)
    page_size = fields.Integer(string='Page Size', default=3)
    total_count = fields.Integer(string='Total Count', readonly=True)
    page_info = fields.Char(string='Page Info', compute='_compute_page_info')

    def _compute_dummy(self):
        for wizard in self:
            wizard.dummy_beneficiaries_field = ""

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

    @api.model
    def get_beneficiaries(self, page, page_size):
        wizard = self.env['g2p.eligibility.summary.wizard'].browse(self.env.context.get('active_id'))
        target_registry_type = wizard.target_registry_type
        _logger.info("Target registry type: %s", target_registry_type)
        all_beneficiaries = [
            {
                "id": 2,
                "unique_id": "DEF456",
                "registration_date": "2025-02-27T15:49:33.450868",
                "name": "Shyam",
                "land_area": 20,
                "no_of_cattle_heads": 0,
                "no_of_poultry_heads": 0
            },
            {
                "id": 3,
                "unique_id": "ABC456",
                "registration_date": "2025-02-27T15:49:33.450868",
                "name": "Govinda",
                "land_area": 0,
                "no_of_cattle_heads": 9,
                "no_of_poultry_heads": 30
            },
            {
                "id": 5,
                "unique_id": "ABC789",
                "registration_date": "2025-02-27T15:49:33.450868",
                "name": "Aditya",
                "land_area": 50,
                "no_of_cattle_heads": 0,
                "no_of_poultry_heads": 700
            },
            {
                "id": 6,
                "unique_id": "ABC739",
                "registration_date": "2025-02-27T15:49:33.450868",
                "name": "Madhu",
                "land_area": 50,
                "no_of_cattle_heads": 0,
                "no_of_poultry_heads": 700
            },
            {
                "id": 7,
                "unique_id": "ABC799",
                "registration_date": "2025-02-27T15:49:33.450868",
                "name": "Sunny",
                "land_area": 50,
                "no_of_cattle_heads": 0,
                "no_of_poultry_heads": 700
            }
        ]
        total_count = len(all_beneficiaries)
        start_index = (page - 1) * page_size
        end_index = start_index + page_size
        beneficiaries = all_beneficiaries[start_index:end_index]
        _logger.info("Beneficiary type: %s", target_registry_type)
        return {
            "message": {
                "total_beneficiary_count": total_count,
                "page": page,
                "page_size": page_size,
                "beneficiaries": beneficiaries,
            },
            "target_registry_type": "farmer",
        }

    @api.depends('target_registry_type', 'beneficiary_search')
    def _compute_summary_lines(self):
        general_keys = ['id', 'program_id', 'program_mnemonic', 'target_registry_type',
                        'que_eee_request_id', 'number_of_registrants', 'date_created']
        statistics_keys = ['age_mean', 'age_quartile_25', 'age_quartile_50', 'age_quartile_75']

        for wizard in self:
            wizard.summary_line_ids = [(5, 0, 0)]
            api_url = self.env['ir.config_parameter'].sudo().get_param('g2p_pbms.eee_api_url')
            if not api_url:
                _logger.error("API_URL not set in environment")
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
                        "que_eee_request_id": 2,
                        "number_of_registrants": 3,
                        "date_created": "2025-02-28T12:24:00.562302",
                        "age_mean": 10.33,
                        "age_quartile_25": 8,
                        "age_quartile_50": 9,
                        "age_quartile_75": 12
                    }
                }
            lines = []
            for key, value in api_response.get('message', {}).items():
                if key in general_keys:
                    lines.append((0, 0, {
                        'wizard_id': wizard.id,
                        'key': key,
                        'value': str(value),
                        'summary_type': 'general'
                    }))
                elif key in statistics_keys:
                    lines.append((0, 0, {
                        'wizard_id': wizard.id,
                        'key': key,
                        'value': str(value),
                        'summary_type': 'statistics'
                    }))
            wizard.summary_line_ids = lines

    @api.depends('summary_line_ids')
    def _compute_general(self):
        for wizard in self:
            wizard.summary_general_line_ids = wizard.summary_line_ids.filtered(
                lambda r: r.summary_type == 'general'
            )

    @api.depends('summary_line_ids')
    def _compute_statistics(self):
        for wizard in self:
            wizard.summary_statistics_line_ids = wizard.summary_line_ids.filtered(
                lambda r: r.summary_type == 'statistics'
            )


class G2PAPISummaryLine(models.TransientModel):
    _name = 'g2p.api.summary.line'
    _description = 'Dynamic API Summary Line'

    wizard_id = fields.Many2one('g2p.eligibility.summary.wizard', string='Wizard')
    key = fields.Char(string='Field')
    value = fields.Text(string='Value')
    summary_type = fields.Selection(
        [('general', 'General'), ('statistics', 'Statistics')],
        string="Summary Type",
        default='general'
    )
