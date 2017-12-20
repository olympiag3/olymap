#!/usr/bin/python
#
# Given a game lib, generate HTML map for all components
#

import olypy.oio as oio
import olypy.dbck as dbck

import olymap.utilities as u
import olymap.ship as ship
import olymap.char as char
import olymap.loc as loc
import olymap.item as itm
import olymap.storm as storm
import olymap.player as player
import olymap.skill as skill
import olymap.reports as reports
import olymap.maps as maps
import olymap.legacy as legacy


def make_map(inlib, outdir, instance):
    inst_dict = {'g2': {'main': [10000, 100, 100], 'hades': [24251, 76, 76], 'faery': [20013, 7, 938]},
                 'g4': {'main': [10000, 80, 80], 'hades': [24000, 50, 50], 'faery': [18000, 46, 46],
                        'cloudlands': [30000, 5, 5]},
                 'qa': {'main': [10000, 10, 10], 'hades': [14000, 7, 7], 'faery': [12000, 10, 10]}}
    data = oio.read_lib(inlib)
    dbck.check_db(data, fix=True, checknames=True)
    if instance == 'g2':
        hades_matrix = legacy.create_hades_matrix(data, inst_dict['g2']['hades'][0])
        faery_matrix = legacy.create_hades_matrix(data, inst_dict['g2']['faery'][0])
    else:
        hades_matrix = []
        faery_matrix = []
    chains = resolve_chains(data)
    write_box_pages(data, chains, outdir, instance, inst_dict)
    write_reports(data, chains, outdir)
    write_maps(data, chains, outdir, instance, inst_dict)


def resolve_chains(data):
    print('Making chains')
    chains = {}
    chains['pledges'] = u.resolve_all_pledges(data)
    chains['prisoners'] = u.resolve_all_prisoners(data)
    chains['hidden'] = u.resolve_hidden_locs(data)
    chains['storms'] = u.resolve_bound_storms(data)
    chains['teaches'] = u.resolve_teaches(data)
    chains['child_skills'] = u.resolve_child_skills(data)
    chains['skills_knowns'] = u.resolve_skills_known(data)
    chains['garrisons'] = u.resolve_garrisons(data)
    chains['trades'] = u.resolve_trades(data)
    chains['castles'] = u.resolve_castles(data)
    return chains


def write_box_pages(data, chains, outdir, instance, inst_dict):
    print('Writing box pages')
    for k, v in data.items():
        if u.return_kind(v) == 'loc':
            loc.write_loc_html(v, k, data, chains['hidden'], chains['garrisons'],
                               chains['trades'], outdir, instance, inst_dict)
        elif u.return_kind(v) == 'char':
            char.write_char_html(v, k, data, chains['pledges'],
                                 chains['prisoners'], outdir, instance)
        elif u.return_kind(v) == 'player':
            player.write_player_html(v, k, data, outdir)
        elif u.return_kind(v) == 'item':
            itm.write_item_html(v, k, data, chains['trades'], outdir)
        elif u.return_kind(v) == 'ship':
            ship.write_ship_html(v, k, data, outdir)
        elif u.return_kind(v) == 'skill':
            skill.write_skill_html(v, k, data, chains['teaches'],
                                   chains['child_skills'], chains['skills_knowns'],
                                   outdir)
        elif u.return_kind(v) == 'storm':
            storm.write_storm_html(v, k, data, chains['storms'], outdir)


def write_reports(data, chains, outdir):
    print('Writing reports')
    reports.ship_report(data, outdir)
    reports.player_report(data, outdir)
    reports.item_report(data, chains['trades'], outdir)
    reports.healing_potion_report(data, outdir)
    reports.orb_report(data, outdir)
    reports.projected_cast_potion_report(data, outdir)
    reports.location_report(data, outdir)
    reports.skill_xref_report(data, chains['teaches'], outdir)
    reports.trade_report(data, chains['trades'], outdir)
    reports.road_report(data, outdir)
    reports.gate_report(data, outdir)
    reports.character_report(data, outdir)
    reports.graveyard_report(data, outdir)
    reports.faeryhill_report(data, outdir)
    reports.castle_report(data, outdir, chains['garrisons'])
    reports.city_report(data, outdir)


def write_maps(data, chains, outdir, instance, inst_dict):
    print('Writing Maps')
    # inst_dict = {'g2': {'main': [10000, 100, 100]},
    #              'g4': {'main': [10000, 80, 80], 'hades': [24000, 50, 50], 'faery': [18000, 46, 46], 'cloudlands': [30000, 5, 5]},
    #              'qa': {'main': [10000, 10, 10], 'hades': [14000, 7, 7], 'faery': [12000, 10, 10]}}
    dimensions = inst_dict[instance]
    maps.write_index(outdir, instance, inst_dict)
    for world in dimensions:
        world_rec = dimensions[world]
        if instance == 'g2' and world in {'faery', 'hades'}:
            pass
        else:
            maps.write_bitmap(outdir,
                             data,
                             world_rec[0],
                             world_rec[1],
                             world_rec[2],
                             world)
            maps.write_top_map(outdir,
                               world_rec[0],
                               world_rec[1],
                               world_rec[2],
                               world)
            maps.write_map_leaves(data,
                                  chains['castles'],
                                  outdir,
                                  world_rec[0],
                                  world_rec[1],
                                  world_rec[2],
                                  world,
                                  instance)
