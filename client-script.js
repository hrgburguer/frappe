frappe.ui.form.on("BOM", {
    refresh(frm) {

        if (frm.doc.docstatus == 1) {

            frm.add_custom_button("Update item sales price", function() {

                frappe.call({
                    method: "update_item_sales_price",
                    args: {
                        bom: frm.doc.name
                    },
                    freeze: true,
                    freeze_message: "Atualizando preço...",
                    callback: function(r) {
                        frappe.show_alert("Preço atualizado.");
                    }
                });

            });

        }

    }
});