frappe.ui.form.on("BOM", {
    refresh(frm) {
        frm.add_custom_button("Update item sales price", function() {
            frappe.prompt(
                [
                    {
                        label: "Calcular preço de",
                        fieldname: "calc_mode",
                        fieldtype: "Select",
                        options: [
                            { label: "Item do BOM (produto final)", value: "bom_item" },
                            { label: "Itens que compõem o BOM (componentes)", value: "component_items" }
                        ],
                        default: "bom_item",
                        reqd: 1
                    },
                    {
                        label: "Item Tax Template",
                        fieldname: "item_tax_template",
                        fieldtype: "Link",
                        options: "Item Tax Template",
                        reqd: 1
                    }
                ],
                function(values) {
                    frappe.call({
                        method: "update_item_sales_price",
                        args: {
                            bom: frm.doc.name,
                            item_tax_template: values.item_tax_template,
                            calc_mode: values.calc_mode
                        },
                        freeze: true,
                        freeze_message: "Atualizando preço...",
                        callback: function(r) {
                            frappe.show_alert("Preço atualizado.");
                        }
                    });
                },
                "Configurar atualização de preço",
                "Atualizar"
            );
        });
    }
});