{
    "name": "PBMS",
    "version": "1.0",
    "summary": "OpenG2P PBMS",
    "description": "OpenG2P PBMS module",
    "category": "OpenG2P",
    "depends": ["base"],
    "data": [
        "security/ir.model.access.csv",
        "views/agency/agencies_view.xml",
        "views/program/program_view.xml",
        "views/registries/student_registry_view.xml",
        "views/registries/farmer_registry_view.xml",
        "views/eligibility_rule/eligibility_rule_view.xml",
    ],
    "installable": True,
    "application": True,
    "auto_install": False,
}
