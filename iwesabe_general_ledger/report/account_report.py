# -*- coding: utf-8 -*-
from odoo import models, fields, api, _


class AccountReport(models.AbstractModel):
    _inherit = 'account.report'

    filter_account_group = None
    filter_move_id = None
    filter_supplier_site = None
    filter_analytic = True



    ####################################################
    # OPTIONS: Account Group
    ####################################################

    @api.model
    def _init_filter_account_group(self, options, previous_options=None):
        if not self.filter_account_group:
            return
        if not self.filter_move_id:
            return
        if not self.filter_supplier_site:
            return

        options['account_group'] = True
        options['account_groups'] = previous_options and previous_options.get('account_groups') or []
        selected_account_groups_ids = [int(partner) for partner in options['account_groups']]
        selected_account_groups = selected_account_groups_ids and self.env['res.partner'].browse(
            selected_account_groups_ids) or self.env[
                                      'account.group']
        options['selected_account_groups_ids'] = selected_account_groups.mapped('name')

        # ================
        options['move_id'] = True
        options['move_ids'] = previous_options and previous_options.get('move_ids') or []
        selected_moves_ids = [int(partner) for partner in options['move_ids']]
        selected_move_id = selected_moves_ids and self.env['res.partner'].browse(
            selected_moves_ids) or self.env[
                                      'account.move']
        options['selected_moves_ids'] = selected_move_id.mapped('name')

        # ================
        options['supplier_site'] = True
        options['supplier_sites'] = previous_options and previous_options.get('supplier_sites') or []
        selected_supplier_sites = [int(partner) for partner in options['supplier_sites']]
        selected_supplier_site = selected_supplier_sites and self.env['res.partner'].browse(
            selected_supplier_sites) or self.env[
                               'site.solution']
        options['selected_supplier_sites'] = selected_supplier_site.mapped('site_supplier_name')

        print(options['selected_supplier_sites'],'LLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLL')


    @api.model
    def _get_options_account_group_domain(self, options):
        domain = []
        if options.get('account_groups'):
            account_groups = [int(group) for group in options['account_groups']]
            domain.append(('account_group', 'in', account_groups))
        if options.get('move_ids'):
            move_ids = [int(group) for group in options['move_ids']]
            domain.append(('move_id', 'in', move_ids))

        if options.get('supplier_sites'):
            supplier_sites = [int(group) for group in options['supplier_sites']]
            domain.append(('supplier_site', 'in', supplier_sites))

        return domain

    @api.model
    def _get_options_domain(self, options):
        domain = super(AccountReport, self)._get_options_domain(options)
        domain += self._get_options_account_group_domain(options)
        return domain

    def get_report_informations(self, options):
        '''
        return a dictionary of informations that will be needed by the js widget, manager_id, footnotes, html of report and searchview, ...
        '''
        options = self._get_options(options)

        searchview_dict = {'options': options, 'context': self.env.context}
        # Check if report needs analytic
        if options.get('analytic_accounts') is not None:
            options['selected_analytic_account_names'] = [self.env['account.analytic.account'].browse(int(account)).name for account in options['analytic_accounts']]
        if options.get('analytic_tags') is not None:
            options['selected_analytic_tag_names'] = [self.env['account.analytic.tag'].browse(int(tag)).name for tag in options['analytic_tags']]

        if options.get('partner'):
            options['selected_partner_ids'] = [self.env['res.partner'].browse(int(partner)).name for partner in options['partner_ids']]
            options['selected_partner_categories'] = [self.env['res.partner.category'].browse(int(category)).name for category in options['partner_categories']]

        # add account_group to filters
        if options.get('account_group'):
            options['selected_account_groups_ids'] = [self.env['account.group'].browse(int(group)).name for group in options['account_groups']]

            # add account_group to filters
        if options.get('move_id'):
            options['selected_moves_ids'] = [self.env['account.move'].browse(int(journal)).name for journal in
                                                      options['move_ids']]
        if options.get('supplier_site'):
            print("TTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTT")
            options['selected_supplier_sites'] = [self.env['site.solution'].browse(int(site)).name for site in
                                                      options['supplier_sites']]

        # Check whether there are unposted entries for the selected period or not (if the report allows it)
        if options.get('date') and options.get('all_entries') is not None:
            date_to = options['date'].get('date_to') or options['date'].get('date') or fields.Date.today()
            period_domain = [('state', '=', 'draft'), ('date', '<=', date_to)]
            options['unposted_in_period'] = bool(self.env['account.move'].search_count(period_domain))

        if options.get('journals'):
            journals_selected = set(journal['id'] for journal in options['journals'] if journal.get('selected'))
            for journal_group in self.env['account.journal.group'].search([('company_id', '=', self.env.company.id)]):
                if journals_selected and journals_selected == set(self._get_filter_journals().ids) - set(journal_group.excluded_journal_ids.ids):
                    options['name_journal_group'] = journal_group.name
                    break


        report_manager = self._get_report_manager(options)
        print(options,"GGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGG")
        info = {'options': options,
                'context': self.env.context,
                'report_manager_id': report_manager.id,
                'footnotes': [{'id': f.id, 'line': f.line, 'text': f.text} for f in report_manager.footnotes_ids],
                'buttons': self._get_reports_buttons_in_sequence(),
                'main_html': self.get_html(options),
                'searchview_html': self.env['ir.ui.view']._render_template(self._get_templates().get('search_template', 'account_report.search_template'), values=searchview_dict),
                }
        return info

