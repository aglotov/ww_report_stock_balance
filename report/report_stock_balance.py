from odoo import fields, models, tools, api


class ReportStockBalance(models.Model):
    _name = 'ww.report.stock.balance'
    _auto = False
    _description = 'Stock Balance Report'

    date = fields.Date(string='Date', readonly=True)
    product_tmpl_id = fields.Many2one('product.template', related='product_id.product_tmpl_id')
    product_id = fields.Many2one('product.product', string='Product', readonly=True)
    product_qty_open = fields.Float(string='Quantity open', readonly=True)
    product_qty_in = fields.Float(string='Quantity in', readonly=True)
    product_qty_out = fields.Float(string='Quantity out', readonly=True)
    product_qty_close = fields.Float(string='Quantity close', readonly=True)
    move_ids = fields.One2many('stock.move', readonly=True)
    company_id = fields.Many2one('res.company', readonly=True)
    warehouse_id = fields.Many2one('stock.warehouse', readonly=True)

    def init(self):
        tools.drop_view_if_exists(self._cr, 'ww_report_stock_balance')
        query = """
CREATE or REPLACE VIEW ww_report_stock_balance AS (
SELECT
    MIN(id) as id,
    product_id,
    state,
    date,
    sum(product_qty) as product_qty,
    company_id,
    warehouse_id
FROM (SELECT
        m.id,
        m.product_id,
        CASE
            WHEN whs.id IS NOT NULL AND whd.id IS NULL THEN 'out'
            WHEN whd.id IS NOT NULL AND whs.id IS NULL THEN 'in'
        END AS state,
        m.date::date AS date,
        CASE
            WHEN whs.id IS NOT NULL AND whd.id IS NULL THEN -m.product_qty
            WHEN whd.id IS NOT NULL AND whs.id IS NULL THEN m.product_qty
        END AS product_qty,
        m.company_id,
        CASE
            WHEN whs.id IS NOT NULL AND whd.id IS NULL THEN whs.id
            WHEN whd.id IS NOT NULL AND whs.id IS NULL THEN whd.id
        END AS warehouse_id
    FROM
        stock_move m
    LEFT JOIN stock_location ls on (ls.id=m.location_id)
    LEFT JOIN stock_location ld on (ld.id=m.location_dest_id)
    LEFT JOIN stock_warehouse whs ON ls.parent_path like concat('%/', whs.view_location_id, '/%')
    LEFT JOIN stock_warehouse whd ON ld.parent_path like concat('%/', whd.view_location_id, '/%')
    LEFT JOIN product_product pp on pp.id=m.product_id
    LEFT JOIN product_template pt on pt.id=pp.product_tmpl_id
    WHERE
        pt.type = 'product' AND
        m.product_qty != 0 AND
        (whs.id IS NOT NULL OR whd.id IS NOT NULL) AND
        (whs.id IS NULL OR whd.id IS NULL OR whs.id != whd.id) AND
        m.state NOT IN ('cancel', 'draft', 'done')
    
UNION ALL
    
SELECT
    
GROUP BY product_id, state, date, company_id, warehouse_id
);
"""
        self.env.cr.execute(query)

    @api.model
    def read_group(self, domain, fields, groupby, offset=0, limit=None, orderby=False, lazy=True):
        for i in range(len(domain)):
            if domain[i][0] == 'product_tmpl_id' and domain[i][1] in ('=', 'in'):
                tmpl = self.env['product.template'].browse(domain[i][2])
                # Avoid the subquery done for the related, the postgresql will plan better with the SQL view
                # and then improve a lot the performance for the forecasted report of the product template.
                domain[i] = ('product_id', 'in', tmpl.with_context(active_test=False).product_variant_ids.ids)
        return super().read_group(domain, fields, groupby, offset, limit, orderby, lazy)
