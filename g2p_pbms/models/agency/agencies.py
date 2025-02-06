from odoo import models, fields, api
import logging

_logger = logging.getLogger(__name__)


class G2PAgencies(models.Model):
    _name = "g2p.agencies"
    _description = "Agencies Model"

    name = fields.Char(string="Name", required=True)
    mnemonic = fields.Text(string="Agency Mnemonic")


class G2PDeliveryClassificationCodes(models.Model):
    _name = "g2p.delivery.classification.codes"
    _description = "Delivery Classification Codes"
    _table = "g2p_delivery_classification_codes"
    _rec_name = "delivery_classification_mnemonic"

    delivery_classification_mnemonic = fields.Char(
        string="Delivery Classification Mnemonic", required=True
    )
    description = fields.Char(string="Description")

    _sql_constraints = [
        (
            "unique_delivery_classification_mnemonic",
            "unique(delivery_classification_mnemonic)",
            "The delivery classification mnemonic must be unique!",
        )
    ]


class G2PDeliveryCodes(models.Model):
    _name = "g2p.delivery.codes"
    _description = "Delivery Codes"
    _table = "g2p_delivery_codes"
    _rec_name = "delivery_mnemonic"

    delivery_mnemonic = fields.Char(string="Delivery Mnemonic", required=True)
    delivery_type = fields.Selection(
        [
            ("COMMODITY", "Commodity"),
            ("SERVICE", "Service"),
            ("COMBINATION", "Combination"),
        ],
        string="Delivery Type",
        required=True,
    )
    delivery_classification_id = fields.Many2one(
        "g2p.delivery.classification.codes",
        string="Delivery Classification",
        required=True,
    )
    delivery_description = fields.Char(string="Delivery Description")

    _sql_constraints = [
        (
            "unique_delivery_mnemonic",
            "unique(delivery_mnemonic)",
            "The delivery mnemonic must be unique!",
        )
    ]

    def action_test_domain(self):
        """
        This method tests a domain on the G2PDeliveryCodes model.
        The domain filters records where:
         - delivery_mnemonic contains 'Test' (case-insensitive)
         - delivery_type is 'SERVICE'
         - delivery_classification_id equals 1
        It then logs the found records and returns an action to open a tree view.
        """
        domain = [
            "&",
            ("delivery_description", "!=", False),
            "|",
            "|",
            "&",
            ("delivery_mnemonic", "ilike", "Test"),
            ("delivery_type", "=", "SERVICE"),
            "&",
            ("delivery_mnemonic", "ilike", "Prod"),
            ("delivery_type", "=", "COMMODITY"),
            ("delivery_classification_id", "=", 2),
        ]
        query = self.get_query(domain)
        records = self.search(domain)
        _logger.info("Query: %s", query)
        _logger.info("Found %s records matching the domain.", len(records))
        for rec in records:
            _logger.info("Record: %s", rec.delivery_mnemonic)

        return {
            "type": "ir.actions.act_window",
            "name": "Test Delivery Codes",
            "res_model": "g2p.delivery.codes",
            "view_mode": "tree,form",
            "domain": domain,
            "target": "current",
        }

    def get_query(self, args, apply_ir_rules=False):

        query = self._where_calc(args)

        if apply_ir_rules:
            self._apply_ir_rules(query, "read")

        from_clause, where_clause, where_clause_params = query.get_sql()

        where_str = where_clause and (" WHERE %s" % where_clause) or ""

        query_str = 'SELECT "%s".id FROM ' % self._table + from_clause + where_str

        where_clause_params = map(lambda x: "'" + str(x) + "'", where_clause_params)

        return query_str % tuple(where_clause_params)


class G2PAgencyDeliveryCodes(models.Model):
    _name = "g2p.agency.delivery.codes"
    _description = "Agency Delivery Codes"
    _table = "g2p_agency_delivery_codes"

    agency_id = fields.Many2one("g2p.agencies", string="Agency", required=True)
    delivery_id = fields.Many2one(
        "g2p.delivery.codes", string="Delivery Code", required=True
    )
