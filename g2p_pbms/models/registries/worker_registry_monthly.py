from odoo import models, fields, api

class G2PWorkerRegistryMonthly(models.Model):
    _name = "g2p.worker.registry.monthly"
    _description = "Worker Registry Monthly"

    unique_id = fields.Integer(string="Unique ID")
    name = fields.Char(string="Name")
    attendance_month = fields.Char(string="Data Collection Month")
    source_type = fields.Char(string="Source Type")
