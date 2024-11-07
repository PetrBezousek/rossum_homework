"""Formatter for XML."""

from lxml import etree
from lxml.etree import Element


def reformat_xml(xml: bytes) -> Element:
    """Take XML bytes and return reformated XML object.

    Example of the format: https://drive.google.com/file/d/1D0phhhui5GkVElAyxi1_KmkO6OJB4_40/view?usp=sharing
    """
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

    for section in root.find("results").find("annotation").find("content").findall("section"):
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
