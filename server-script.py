bom_name = frappe.form_dict.get("bom")

if not bom_name:
    frappe.throw("BOM não informado.")

bom = frappe.get_doc("BOM", bom_name)

item_code = bom.item
cost = bom.total_cost

frappe.msgprint(f"Custo: {cost}")

# -------------------------------------------------------------------
# ITEM
# -------------------------------------------------------------------

item = frappe.get_doc("Item", item_code)

# -------------------------------------------------------------------
# SOMA DAS TAXAS
# -------------------------------------------------------------------

tax_percent = 0

for item_tax in item.taxes:
    template = frappe.get_doc(
        "Item Tax Template",
        item_tax.item_tax_template
    )

    for tax in template.taxes:
        frappe.msgprint(f"Taxa: {tax.tax_rate}")
        tax_percent += tax.tax_rate

# -------------------------------------------------------------------
# CÁLCULO
# -------------------------------------------------------------------

if tax_percent:
    price = cost / (1 - (tax_percent / 100))

price = round(price, 2)

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

    frappe.db.set_value(
        "Item Price",
        existing[0].name,
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

frappe.db.commit()

frappe.msgprint(f"Preço atualizando utilizando custo {cost} e taxa total de {tax_percent}. Preço final: {price}")

frappe.response["message"] = f"Preço atualizado para {price}"