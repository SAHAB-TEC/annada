# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models


class BarcodeProductLabels25_40(models.AbstractModel):
    _name = 'report.report_product_validity.barcode_product_validity'
    _description = "Product Validity Report"

    @api.model
    def _get_report_values(self, docids, data=None):
        barcode_labels_report = self.env['ir.actions.report']._get_report_from_name(
            'report_product_validity.barcode_product_validity')
        barcode_labels = data['form']['barcode_labels']
        print("barcode_labels_report ==> ", barcode_labels_report)
        print("barcode_labels ==> ", barcode_labels)
        barcode_labels = self.env['stock.lot'].browse(barcode_labels)
        print("barcode_labels ==> ", barcode_labels)
        return {
            'doc_ids': barcode_labels,
            'doc_model': barcode_labels_report.model,
            'docs': barcode_labels,
            'data': data,
        }
