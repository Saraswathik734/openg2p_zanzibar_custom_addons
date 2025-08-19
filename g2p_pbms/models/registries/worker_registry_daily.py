from odoo import models, fields, api

class G2PWorkerRegistryDaily(models.Model):
    _name = "g2p.worker.registry.daily"
    _description = "Worker Registry Daily"

    unique_id = fields.Integer(string="Unique ID")

    nrc_number = fields.Char(string="NRC Number")
    attendance_date = fields.Date(string="Attendance Date")
    task = fields.Text(string="Task")