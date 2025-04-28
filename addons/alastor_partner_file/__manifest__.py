{
    "name": "Partner File",
    "version": "13.0.0.0.1",
    "category": "Sale",
    "summary": """

Client Files
======================================================================


Version 0.1
-------------


    """,
    "author": "ADATECS.surl",
    "website": "https://www.desoft.cu",
    "license": "LGPL-3",
    "installable": True,
    "depends": ["alastor_partner_contract"],
    "init_xml": [],
    "data": [
        "views/views.xml",
        "security/ir.model.access.csv",
        "report/reports.xml",
        "report/report_client_file.xml",
        "report/report_client_file_proform.xml",
    ],
    "application": False,
}
