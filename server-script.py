bom_name = frappe.form_dict.get("bom")
item_tax_template_name = frappe.form_dict.get("item_tax_template")
calc_mode = frappe.form_dict.get("calc_mode") or "bom_item"

if not bom_name:
    frappe.throw("BOM não informado.")
if not item_tax_template_name:
    frappe.throw("Item Tax Template não informado.")

bom = frappe.get_doc("BOM", bom_name)

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
# SOMA DAS TAXAS (Template selecionado pelo usuário)
# -------------------------------------------------------------------
def calculate_price(cost, template_name):
    result = {}
    tax_percent = 0
    round_up = False
    template = frappe.get_doc("Item Tax Template", template_name)
    for tax in template.taxes:
        frappe.msgprint(f"{tax.tax_type}: {tax.tax_rate}")
        if tax.tax_type in (
            "Campanha Inteligente - HB",
            "Contabilidade - HB",
            "INSS sobre Pró-labore - HB",
            "Mensalidade - HB",
        ):
            cost = cost + tax.tax_rate
        elif tax.tax_type == "Arredondar - HB":
            round_up = True
        else:
            tax_percent = tax_percent + tax.tax_rate

    price = cost
    if tax_percent:
        price = cost / (1 - (tax_percent / 100))
    if round_up:
        price = -(-price // 5) * 5

    result["cost"] = cost
    result["tax_percent"] = tax_percent
    result["price"] = price
    return result

# -------------------------------------------------------------------
# ITEM PRICE (cria ou atualiza) + aplica tags do BOM
# -------------------------------------------------------------------
def upsert_item_price(item_code, price, price_list="Standard Selling"):
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

    for tag in bom_tags:
        add_tag_safe(tag, "Item Price", item_price_name)

    return item_price_name

# -------------------------------------------------------------------
# MODO 1: Preço do item do BOM (produto final), usando o custo total do BOM
# -------------------------------------------------------------------
def process_bom_item():
    item_code = bom.item
    cost = bom.total_cost
    frappe.msgprint(f"CMV: {cost}")

    calc = calculate_price(cost, item_tax_template_name)

    upsert_item_price(item_code, calc["price"])

    frappe.msgprint(f"Custo Fixo Final: R${calc['cost']}")
    frappe.msgprint(f"Taxa Total Final: {calc['tax_percent']}%")
    frappe.msgprint(f"Preço Final: R${calc['price']}")

    return f"Preço atualizado para {calc['price']}"

# -------------------------------------------------------------------
# MODO 2: Preço de cada item componente do BOM, usando o custo de cada linha
# -------------------------------------------------------------------
def process_component_items():
    results = []
    for row in bom.items:
        item_code = row.item_code
        cost = row.amount or 0

        calc = calculate_price(cost, item_tax_template_name)

        upsert_item_price(item_code, calc["price"])

        frappe.msgprint(f"{item_code} | Custo: R${calc['cost']} | Taxa: {calc['tax_percent']}% | Preço: R${calc['price']}")
        results.append(f"{item_code}: {calc['price']}")

    return "Preços atualizados:\n" + "\n".join(results)

# -------------------------------------------------------------------
# EXECUÇÃO CONFORME O MODO ESCOLHIDO
# -------------------------------------------------------------------
if calc_mode == "component_items":
    message = process_component_items()
else:
    message = process_bom_item()

frappe.db.commit()
frappe.response["message"] = message