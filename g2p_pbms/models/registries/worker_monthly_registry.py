from odoo import models, fields, api

class G2PWorkerMonthlyRegistry(models.Model):
    _name = "g2p.worker.monthly.registry"
    _description = "Worker Monthly Registry"

    unique_id = fields.Integer(string="Unique ID")
    name = fields.Char(string="Name")
    attendance_month = fields.Char(string="Data Collection Month")
    source_type = fields.Char(string="Source Type")
