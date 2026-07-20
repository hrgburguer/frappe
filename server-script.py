bom_name = frappe.form_dict.get("bom")
item_tax_template_name = frappe.form_dict.get("item_tax_template")
if not bom_name:
    frappe.throw("BOM não informado.")
if not item_tax_template_name:
    frappe.throw("Item Tax Template não informado.")
round_up = False
bom = frappe.get_doc("BOM", bom_name)
item_code = bom.item
cost = bom.total_cost
frappe.msgprint(f"CMV: {cost}")

# -------------------------------------------------------------------
# TAGS DO BOM
# -------------------------------------------------------------------
bom_tags_raw = bom.get("_user_tags") or ""
bom_tags = [t.strip() for t in bom_tags_raw.split(",") if t.strip()]

def add_tag_safe(tag, doctype, docname):
    tag = tag.strip()
    if not tag:
        return
    if not frappe.db.exists("Tag", tag):
        frappe.get_doc({
            "doctype": "Tag",
            "name": tag
        }).insert(ignore_permissions=True)
    if not frappe.db.exists("Tag Link", {
        "document_type": doctype,
        "document_name": docname,
        "tag": tag
    }):
        frappe.get_doc({
            "doctype": "Tag Link",
            "document_type": doctype,
            "document_name": docname,
            "tag": tag
        }).insert(ignore_permissions=True)

# -------------------------------------------------------------------
# ITEM
# -------------------------------------------------------------------
item = frappe.get_doc("Item", item_code)

# -------------------------------------------------------------------
# SOMA DAS TAXAS (Template selecionado pelo usuário)
# -------------------------------------------------------------------
tax_percent = 0
template = frappe.get_doc("Item Tax Template", item_tax_template_name)
for tax in template.taxes:
    frappe.msgprint(f"{tax.tax_type}: {tax.tax_rate}")
    if tax.tax_type == "Mensalidade - HB" or tax.tax_type == "Contabilidade - HB":
        cost += tax.tax_rate
    elif tax.tax_type == "Arredondar - HB":
        round_up = True
    else:
        tax_percent += tax.tax_rate

# -------------------------------------------------------------------
# CÁLCULO
# -------------------------------------------------------------------
price = cost
if tax_percent:
    price = cost / (1 - (tax_percent / 100))
if round_up:
    price = -(-price // 5) * 5

# -------------------------------------------------------------------
# ITEM PRICE
# -------------------------------------------------------------------
price_list = "Standard Selling"
existing = frappe.get_all(
    "Item Price",
    filters={
        "item_code": item_code,
        "price_list": price_list
    },
    fields=["name"],
    limit=1
)

if existing:
    item_price_name = existing[0].name
    frappe.db.set_value(
        "Item Price",
        item_price_name,
        "price_list_rate",
        price
    )
else:
    doc = frappe.get_doc({
        "doctype": "Item Price",
        "item_code": item_code,
        "price_list": price_list,
        "price_list_rate": price
    })
    doc.insert(ignore_permissions=True)
    item_price_name = doc.name

# -------------------------------------------------------------------
# APLICA AS TAGS DO BOM NO ITEM PRICE
# -------------------------------------------------------------------
for tag in bom_tags:
    add_tag_safe(tag, "Item Price", item_price_name)

frappe.db.commit()

frappe.msgprint(f"Custo Fixo Final: R${cost}")
frappe.msgprint(f"Taxa Total Final: {tax_percent}%")
frappe.msgprint(f"Preço Final: R${price}")
frappe.response["message"] = f"Preço atualizado para {price}"