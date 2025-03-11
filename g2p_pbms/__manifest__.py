{
    "name": "PBMS",
    "version": "1.0",
    "summary": "OpenG2P PBMS",
    "description": "OpenG2P PBMS module",
    "category": "OpenG2P",
    "depends": ["base_setup", "web"],
    "data": [
        "security/ir.model.access.csv",
        "views/agency/agencies_view.xml",
        "views/program/program_view.xml",
        "views/registries/student_registry_view.xml",
        "views/registries/farmer_registry_view.xml",
        "views/eligibility_rule/eligibility_rule_view.xml",
        "views/eligibility_summary/eligibility_summary_view.xml",
        "views/program_eligibility_list/eligibility_request_que_view.xml",
        
    ],
    "assets": {
        "web.assets_backend": [
            "/g2p_pbms/static/src/css/custom_styles.scss",
            "/g2p_pbms/static/src/js/beneficiaries_widget.js",
            "/g2p_pbms/static/src/xml/g2p_beneficiaries_info_tpl.xml"
        ],
    },
    "installable": True,
    "application": True,
    "auto_install": False,
}
