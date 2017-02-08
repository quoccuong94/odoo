# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _
from odoo.addons.website.models.website import slug


class Event(models.Model):
    _inherit = "event.event"

    track_ids = fields.One2many('event.track', 'event_id', 'Tracks')
    track_count = fields.Integer('Tracks', compute='_compute_track_count')

    sponsor_ids = fields.One2many('event.sponsor', 'event_id', 'Sponsors')
    sponsor_count = fields.Integer('Sponsors', compute='_compute_sponsor_count')

    website_track = fields.Boolean('Tracks on Website', compute='_compute_website_track', inverse='_set_website_menu')
    website_track_proposal = fields.Boolean('Proposals on Website', compute='_compute_website_track_proposal', inverse='_set_website_menu')

    allowed_track_tag_ids = fields.Many2many('event.track.tag', relation='event_allowed_track_tags_rel', string='Available Track Tags')
    tracks_tag_ids = fields.Many2many(
        'event.track.tag', relation='event_track_tags_rel', string='Track Tags',
        compute='_compute_tracks_tag_ids', store=True)

    @api.multi
    def _compute_track_count(self):
        data = self.env['event.track'].read_group([('stage_id.is_cancel', '!=', True)], ['event_id'], ['event_id'])
        result = dict((data['event_id'][0], data['event_id_count']) for data in data)
        for event in self:
            event.track_count = result.get(event.id, 0)

    @api.multi
    def _compute_sponsor_count(self):
        data = self.env['event.sponsor'].read_group([], ['event_id'], ['event_id'])
        result = dict((data['event_id'][0], data['event_id_count']) for data in data)
        for event in self:
            event.sponsor_count = result.get(event.id, 0)

    @api.multi
    def _compute_website_track(self):
        for event in self:
            existing_pages = event.menu_id.child_id.mapped('name')
            event.website_track = _('Talks') in existing_pages

    @api.multi
    def _compute_website_track_proposal(self):
        for event in self:
            existing_pages = event.menu_id.child_id.mapped('name')
            event.website_track_proposal = _('Talk Proposals') in existing_pages

    @api.multi
    @api.depends('track_ids.tag_ids')
    def _compute_tracks_tag_ids(self):
        for event in self:
            event.tracks_tag_ids = event.track_ids.mapped('tag_ids').ids

    def _get_menu_entries(self):
        self.ensure_one()
        res = super(Event, self)._get_menu_entries()
        if self.website_track:
            res += [
                (_('Talks'), '/event/%s/track' % slug(self), False),
                (_('Agenda'), '/event/%s/agenda' % slug(self), False)]
        if self.website_track_proposal:
            res += [(_('Talk Proposals'), '/event/%s/track_proposal' % slug(self), False)]
        return res
