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
    if tax.tax_type == "INSS sobre Pró-labore - HB" or tax.tax_type == "Contabilidade - HB" or tax.tax_type == "Mensalidade - HB" or tax.tax_type == "Campanha Inteligente do Ifood - HB" :
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
    # Arredonda para cima em múltiplos de 5 (ex: 62 -> 65, 67 -> 70)
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
frappe.msgprint(f"Custo Fixo Final: R${cost}")
frappe.msgprint(f"Taxa Total Final: {tax_percent}%")
frappe.msgprint(f"Preço Final: R${price}")
frappe.response["message"] = f"Preço atualizado para {price}"