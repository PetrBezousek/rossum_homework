import os
from lxml import etree


from flask import Flask, g, jsonify
from flask_httpauth import HTTPBasicAuth
from werkzeug.security import generate_password_hash, check_password_hash
from flask_expects_json import expects_json

import requests
app = Flask(__name__)
auth = HTTPBasicAuth()


EXPORT_USERNAME = os.getenv("EXPORT_USERNAME", "user")
EXPORT_PASSWORD = os.getenv("EXPORT_PASSWORD", "scrypt:32768:8:1$NL9LWYedZNqirIi1$565535791a13eca917c0b402ffd7135e6c6ef2c13959448ccd87e8f8414f1ea0d75787ed014bb159a796190d5cf9b5bd32e770b7c15f8f92f34fc4d0b5b5912a")

SCHEMA = {
    'type': 'object',
    'properties': {
        'annotation_id': {'type': 'integer'},
        'queue_id': {'type': 'integer'},
    },
    'required': ['annotation_id', 'queue_id']
}

# Verify password function
@auth.verify_password
def verify_password(username, password):
    if username == EXPORT_USERNAME and check_password_hash(EXPORT_PASSWORD, password):
        return username
    return None

@app.route('/export', methods=["POST"])
@auth.login_required
@expects_json(SCHEMA)
def export():
    print(g.data)
    rossum_login = {
        "username": "petrbezousek@email.cz",
        "password": "DGJfNUW@zuh#jlB4*Lcrs3",
    }
    # rossum_key = requests.post('https://bezza.rossum.app/api/v1/auth/login', json=rossum_login).json()
    rossum_key = {'key': '6eb5788f269fe4900f950d45b7a507d949891cff', 'domain': 'bezza.rossum.app'}
    print(rossum_key)
    headers = {
        "Authorization": f"Bearer {rossum_key['key']}"
    }
    params = {
        "format": "xml",
        "id": g.data["annotation_id"],
    }
    rossum_export_data = requests.get(f'https://bezza.rossum.app/api/v1/queues/{g.data["queue_id"]}/export', params=params, headers=headers)

    print(rossum_export_data)
    print(rossum_export_data.status_code)


    # Create the root element
    create_root = etree.Element("InvoiceRegisters")
    invoices = etree.SubElement(create_root, "Invoices")
    payable = etree.SubElement(invoices, "Payable")
    invoice_number = etree.SubElement(payable, "InvoiceNumber")
    invoice_date = etree.SubElement(payable, "InvoiceDate")
    due_date = etree.SubElement(payable, "DueDate")
    total_amount = etree.SubElement(payable, "TotalAmount")
    notes = etree.SubElement(payable, "Notes")
    iban = etree.SubElement(payable, "Iban")
    amount = etree.SubElement(payable, "Amount")
    xml_currency = etree.SubElement(payable, "Currency")
    vendor = etree.SubElement(payable, "Vendor")
    vendor_address = etree.SubElement(payable, "VendorAddress")
    details = etree.SubElement(payable, "Details")

    def add_detail(amount=None, account_id=None, quantity=None, notes=None):

        detail = etree.SubElement(details, "Detail")
        xml_amount = etree.SubElement(detail, "Amount")
        xml_amount.text = amount

        xml_account_id = etree.SubElement(detail, "AccountId")
        xml_account_id.text = account_id

        xml_quantity = etree.SubElement(detail, "Quantity")
        xml_quantity.text = quantity

        xml_notes = etree.SubElement(detail, "Notes")
        xml_notes.text = notes

    root = etree.fromstring(rossum_export_data.content)

    # Access each book in the catalog
    for section in root.find("results").find("annotation").find("content").findall("section"):
        print(section)
        match section.get("schema_id"):
            case "basic_info_section":
                for datapoint in section.findall("datapoint"):
                    match datapoint.get("schema_id"):
                        case "order_id":
                            invoice_number.text = datapoint.text
                        case "date_issue":
                            invoice_date.text = datapoint.text
            case "totals_section":
                for datapoint in section.findall("datapoint"):
                    match datapoint.get("schema_id"):
                        case "amount_due":
                            total_amount.text = datapoint.text
                        case "currency":
                            xml_currency.text = datapoint.text
            case "supplier_section":
                for datapoint in section.findall("datapoint"):
                    match datapoint.get("schema_id"):
                        case "sender_name":
                            vendor.text = datapoint.text
                        case "sender_address":
                            vendor_address.text = datapoint.text
            case "line_items_section":
                for tuple in section.find("multivalue").findall("tuple"):
                    for datapoint in tuple.findall("datapoint"):
                        item_description = None
                        item_quantity = None
                        item_amount_total = None
                        match datapoint.get("schema_id"):
                            case "item_description":
                                item_description = datapoint.text
                            case "item_quantity":
                                item_quantity = datapoint.text
                            case "item_amount_total":
                                item_amount_total = datapoint.text
                        add_detail(amount=item_amount_total, account_id=None, quantity=item_quantity, notes=item_description)


    # Generate a pretty XML string
    xml_string = etree.tostring(create_root, pretty_print=True).decode("utf-8")
    print(xml_string)

    # TODO now send it to paste bin

    return jsonify({
        "success": True,
    })