frappe.ui.form.on("BOM", {
    refresh(frm) {
        frm.add_custom_button("Update item sales price", function() {
            frappe.prompt(
                [
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
                            item_tax_template: values.item_tax_template
                        },
                        freeze: true,
                        freeze_message: "Atualizando preço...",
                        callback: function(r) {
                            frappe.show_alert("Preço atualizado.");
                        }
                    });
                },
                "Selecione o Item Tax Template",
                "Atualizar"
            );
        });
    }
});