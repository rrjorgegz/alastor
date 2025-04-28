FROM odoo:13.0

USER root

COPY ./addons /mnt/extra-addons
COPY ./config/odoo.conf /etc/odoo/odoo.conf
COPY ./requirements.txt /requirements.txt
RUN pip3 install -r /requirements.txt
