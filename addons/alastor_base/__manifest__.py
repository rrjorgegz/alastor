{
    "name": "Alastor Base",
    "version": "13.0.0.0.1",
    "category": "Base",
    "summary": """

Base Alastor
======================================================================




    """,
    "author": "ADATECS.surl",
    "website": "https://www.desoft.cu",
    "license": "LGPL-3",
    "installable": True,
    "depends": ["base", "base_setup", "web_editor", "web_unsplash"],
    "init_xml": [],
    "data": [
        "views/res_partner_views.xml",
        "security/ir.model.access.csv",
        "data/states_municipalities_data.xml",
        "data/res_lang_data.xml",
        "data/res_currency_data.xml",
        "data/res_company_data.xml",
    ],
    "test": [],
    "application": False,
}
