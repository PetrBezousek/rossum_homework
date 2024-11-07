import base64

import flask
import requests
import structlog
from lxml.etree import Element

import config

from flask import Flask, g, jsonify
from flask_expects_json import expects_json
from flask_httpauth import HTTPBasicAuth
from lxml import etree
from werkzeug.security import check_password_hash, generate_password_hash
from config import EXPORT_PASSWORD, EXPORT_USERNAME, ROSSUM_PASSWORD, ROSSUM_USERNAME

config.configure_structlog()
logger = structlog.get_logger()

app = Flask(__name__)
auth = HTTPBasicAuth()


SCHEMA = {
    "type": "object",
    "properties": {
        "annotation_id": {"type": "integer"},
        "queue_id": {"type": "integer"},
    },
    "required": ["annotation_id", "queue_id"],
}


@app.route("/export", methods=["POST"])
@auth.login_required
@expects_json(SCHEMA)
def export() -> flask.wrappers.Response:
    logger.info("export.request", data=g.data)
    is_success = True
    try:
        content = get_export_content()
        generated_xml = reformat_xml(content)
        send_to_postbin(generated_xml)
    except Exception:
        logger.exception("export.exception")
        is_success = False

    return jsonify(
        {
            "success": is_success,
        }
    )


@auth.verify_password
def verify_password(username: str, password: str) -> bool | None:
    if username == EXPORT_USERNAME and check_password_hash(
        generate_password_hash(EXPORT_PASSWORD), password
    ):
        return True
    return None


def get_rossum_auth_header() -> dict:
    """Get necessary headers for rossum API request.

    Get credentials from env variables.
    """
    rossum_login = {
        "username": ROSSUM_USERNAME,
        "password": ROSSUM_PASSWORD,
    }
    rossum_key = requests.post(
        "https://bezza.rossum.app/api/v1/auth/login", json=rossum_login
    ).json()
    headers = {"Authorization": f"Bearer {rossum_key['key']}"}
    return headers


def get_export_content() -> bytes:
    params = {
        "format": "xml",
        "id": g.data["annotation_id"],
    }
    logger.info(
        "export.get_export",
        queue_id=g.data["queue_id"],
        annotation_id=g.data["annotation_id"],
    )
    rossum_export_data = requests.get(
        f'https://bezza.rossum.app/api/v1/queues/{g.data["queue_id"]}/export',
        params=params,
        headers=get_rossum_auth_header(),
    )
    rossum_export_data.raise_for_status()
    return rossum_export_data.content


def reformat_xml(xml: bytes) -> Element:
    # Create the root element
    xml_root = etree.Element("InvoiceRegisters")
    invoices = etree.SubElement(xml_root, "Invoices")
    payable = etree.SubElement(invoices, "Payable")
    invoice_number = etree.SubElement(payable, "InvoiceNumber")
    invoice_date = etree.SubElement(payable, "InvoiceDate")
    due_date = etree.SubElement(payable, "DueDate")
    total_amount = etree.SubElement(payable, "TotalAmount")
    notes = etree.SubElement(payable, "Notes")
    iban = etree.SubElement(payable, "Iban")
    xml_currency = etree.SubElement(payable, "Currency")
    vendor = etree.SubElement(payable, "Vendor")
    vendor_address = etree.SubElement(payable, "VendorAddress")
    details = etree.SubElement(payable, "Details")

    def add_detail(
        amount: str = None,
        account_id: str = None,
        quantity: str = None,
        notes: str = None,
    ) -> None:
        """Add detail to the details element"""
        detail = etree.SubElement(details, "Detail")
        xml_amount = etree.SubElement(detail, "Amount")
        xml_amount.text = amount

        xml_account_id = etree.SubElement(detail, "AccountId")
        xml_account_id.text = account_id

        xml_quantity = etree.SubElement(detail, "Quantity")
        xml_quantity.text = quantity

        xml_notes = etree.SubElement(detail, "Notes")
        xml_notes.text = notes

    root = etree.fromstring(xml)

    for section in (
        root.find("results").find("annotation").find("content").findall("section")
    ):
        match section.get("schema_id"):
            case "basic_info_section":
                for datapoint in section.findall("datapoint"):
                    match datapoint.get("schema_id"):
                        case "order_id":
                            invoice_number.text = datapoint.text
                        case "date_issue":
                            invoice_date.text = datapoint.text
                        case "due_date":  # Guessing the place and name as my sample data do not have it
                            due_date.text = datapoint.text
                        case "iban":  # Guessing the place and name as my sample data do not have it
                            iban.text = datapoint.text
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
                for item_tuple in section.find("multivalue").findall("tuple"):
                    for datapoint in item_tuple.findall("datapoint"):
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
                        add_detail(
                            amount=item_amount_total,
                            account_id=None,
                            quantity=item_quantity,
                            notes=item_description,
                        )
            case "other_section":
                for datapoint in item_tuple.findall("datapoint"):
                    match datapoint.get("schema_id"):
                        case "notes":
                            notes.text = datapoint.text

    return xml_root


def send_to_postbin(xml: Element) -> None:
    """Create a new post-bin and send given XML there."""
    response = requests.post("https://www.postb.in/api/bin").json()

    postbin_data = {
        "annotation_id": g.data["annotation_id"],
        "content": base64.b64encode(etree.tostring(xml, pretty_print=True)).decode(
            "ascii"
        ),
    }
    logger.info("export.send_to_postbin", bin_id=response["binId"], data=postbin_data)
    response = requests.post(
        f"https://www.postb.in/{response['binId']}", json=postbin_data
    )
    response.raise_for_status()
