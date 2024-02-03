# -*- coding: utf-8 -*-

{
    "name": "Alastor Partner Contracts",
    "version": "0.1",
    "author": "Yerandy Reyes Fabregat (yerandy.reyes@desoft.cu)",
    "website": "",
    "category": "Contracts",
    "depends": ["alastor_base", "mail"],
    "description": """

Partner contracts
======================================================================
    """,
    "data": [
        "security/partner_contract_security.xml",
        "security/ir.model.access.csv",
        "report/report_sale_frame_contract.xml",
        "report/partner_contract_reports.xml",
        "data/contract_types_data.xml",
        "data/banks_data.xml",
        "data/purchase_email_template_data.xml",
        "data/sale_email_template_data.xml",
        #'data/cron_data.xml',
        "data/sequences_data.xml",
        "data/subordination_levels_data.xml",
        "report/report_purchase_docs.xml",
        ##'report/report_sale_docs.xml',
        "views/contract_menu_view.xml",
        "wizard/purchase_docs_view.xml",
        ##'wizard/sale_docs_view.xml',
        ##'views/partner_view.xml',
        "views/company_view.xml",
        "views/contract_type_view.xml",
        "views/sale_supplement_view.xml",
        "views/sale_contract_view.xml",
        "views/authorized_signature_view.xml",
        "views/organism_view.xml",
        "views/sale_frame_contract_view.xml",
        "views/purchase_supplement_view.xml",
        "views/purchase_contract_view.xml",
        "views/purchase_frame_contract_view.xml",
        "views/res_config_view.xml",
        "views/mail_alerter_view.xml",
    ],
    "demo": [],
    "test": [],
    "installable": True,
    "auto_install": False,
    "application": True,
    "images": [],
}
