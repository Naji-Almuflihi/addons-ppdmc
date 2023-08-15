# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.tools.misc import format_date, DEFAULT_SERVER_DATE_FORMAT


class AccountMoveLine(models.Model):
    _inherit = "account.move.line"
    # account_group = fields.Many2one(related='account_id.group_id', store=True)



class AccountGeneralLedgerReport(models.AbstractModel):
    _inherit = "account.general.ledger"
    # to show filters in general ledgers
    filter_partner = True
    filter_account_group = True
    filter_move_id = True

    @api.model
    def _get_columns_name(self, options):
        return [

            {'name': ''},
            {'name': _('Date'), 'class': 'date'},
            {'name': _('Communication')},
            {'name': _('Partner')},
            {'name': _('move_id')},
            {'name': _('Account Group')},
            {'name': _('Currency'), 'class': 'number'},
            {'name': _('Debit'), 'class': 'number'},
            {'name': _('Credit'), 'class': 'number'},
            {'name': _('Balance'), 'class': 'number'},
        ]

    @api.model
    def _get_query_amls(self, options, expanded_account, offset=None, limit=None):
        ''' Construct a query retrieving the account.move.lines when expanding a report line with or without the load
        more.
        :param options:             The report options.
        :param expanded_account:    The account.account record corresponding to the expanded line.
        :param offset:              The offset of the query (used by the load more).
        :param limit:               The limit of the query (used by the load more).
        :return:                    (query, params)
        '''

        unfold_all = options.get('unfold_all') or (self._context.get('print_mode') and not options['unfolded_lines'])

        # Get sums for the account move lines.
        # period: [('date' <= options['date_to']), ('date', '>=', options['date_from'])]
        if expanded_account:
            domain = [('account_id', '=', expanded_account.id)]
        elif unfold_all:
            domain = []
        elif options['unfolded_lines']:
            domain = [('account_id', 'in', [int(line[8:]) for line in options['unfolded_lines']])]

        new_options = self._force_strict_range(options)
        tables, where_clause, where_params = self._query_get(new_options, domain=domain)
        ct_query = self.env['res.currency']._get_query_currency_table(options)
        query = '''
                    SELECT
                        account_move_line.id,
                        account_move_line.date,
                        account_move_line.date_maturity,
                        account_move_line.name,
                        account_move_line.ref,
                        account_move_line.company_id,
                        account_move_line.account_id,
                        account_move_line.move_id,                

                        account_move_line.payment_id,
                        account_move_line.move_id,
                        account_move_line.partner_id,
                        account_move_line.currency_id,
                        account_move_line.amount_currency,
                        ROUND(account_move_line.debit * currency_table.rate, currency_table.precision)   AS debit,
                        ROUND(account_move_line.credit * currency_table.rate, currency_table.precision)  AS credit,
                        ROUND(account_move_line.balance * currency_table.rate, currency_table.precision) AS balance,
                        account_move_line__move_id.name         AS move_name,
                        company.currency_id                     AS company_currency_id,
                        partner.name                            AS partner_name,
                        move_id.name                            AS move_id,
                        account_move_line__move_id.move_type         AS move_type,
                         move_id.name                           AS move_id,
                        account.code                            AS account_code,
                        account.name                            AS account_name,
                        journal.code                            AS journal_code,
                        journal.name                            AS journal_name,
                        full_rec.name                           AS full_rec_name
                    FROM account_move_line
                    LEFT JOIN account_move account_move_line__move_id ON account_move_line__move_id.id = account_move_line.move_id
                    LEFT JOIN %s ON currency_table.company_id = account_move_line.company_id
                    LEFT JOIN res_company company               ON company.id = account_move_line.company_id
                    LEFT JOIN res_partner partner               ON partner.id = account_move_line.partner_id
                    LEFT JOIN account_move move_id              ON move_id.id = account_move_line.move_id

                    LEFT JOIN account_account account           ON account.id = account_move_line.account_id
                    LEFT JOIN account_journal journal           ON journal.id = account_move_line.journal_id
                    LEFT JOIN account_full_reconcile full_rec   ON full_rec.id = account_move_line.full_reconcile_id
                    WHERE %s
                    ORDER BY account_move_line.date, account_move_line.id
                ''' % (ct_query, where_clause)




        if offset:
            query += ' OFFSET %s '
            where_params.append(offset)
        if limit:
            query += ' LIMIT %s '
            where_params.append(limit)

        return query, where_params

    @api.model
    def _get_aml_line(self, options, account, aml, cumulated_balance):
        if aml['payment_id']:
            caret_type = 'account.payment'
        elif aml['move_type'] in ('in_refund', 'in_invoice', 'in_receipt'):
            caret_type = 'account.invoice.in'
        elif aml['move_type'] in ('out_refund', 'out_invoice', 'out_receipt'):
            caret_type = 'account.invoice.out'
        else:
            caret_type = 'account.move'

        if aml['ref'] and aml['name']:
            title = '%s - %s' % (aml['name'], aml['ref'])
        elif aml['ref']:
            title = aml['ref']
        elif aml['name']:
            title = aml['name']
        else:
            title = ''

        if aml['currency_id']:
            currency = self.env['res.currency'].browse(aml['currency_id'])
        else:
            currency = False

        return {
            'id': aml['id'],
            'caret_options': caret_type,
            'class': 'top-vertical-align',
            'parent_id': 'account_%d' % aml['account_id'],
            'name': aml['move_name'],
            'columns': [
                {'name': format_date(self.env, aml['date']), 'class': 'date'},
                {'name': self._format_aml_name(aml['name'], aml['ref'], aml['move_name']), 'title': title,
                 'class': 'whitespace_print'},
                {'name': aml['partner_name'], 'title': aml['partner_name'], 'class': 'whitespace_print'},
                {'name': aml['move_id'], 'title': aml['move_id'], 'class': 'whitespace_print'},
                {'name': currency and self.format_value(aml['amount_currency'], currency=currency,
                                                        blank_if_zero=True) or '', 'class': 'number'},
                {'name': self.format_value(aml['debit'], blank_if_zero=True), 'class': 'number'},
                {'name': self.format_value(aml['credit'], blank_if_zero=True), 'class': 'number'},
                {'name': self.format_value(cumulated_balance), 'class': 'number'},
            ],
            'level': 4,
        }

    # def _get_templates(self):
    #     return {
    #             'main_template': 'account_reports.main_template',
    #             'main_table_header_template': 'account_reports.main_table_header',
    #             'line_template': 'account_reports.line_template',
    #             'footnotes_template': 'account_reports.footnotes_template',
    #             'search_template': 'account_reports.search_template',
    #     }


