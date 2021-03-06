#!/usr/bin/python
import pathlib
from pngcanvas import *
import olymap.utilities as u
import olymap.maps as maps
import math
from olypy.oid import to_oid

def create_map_matrix(data, startingpoint):
    # startingpoint = '24251'
    keepon = True
    map_matrix = []
    map_matrix.append([])
    map_matrix[0].append(str(startingpoint))
    row = 0
    col = 0
    while keepon:
        map_cell = data[str(startingpoint)]
        if 'LO' in map_cell and 'pd' in map_cell['LO']:
            dest_list = map_cell['LO']['pd']
            if dest_list[2] != '0':
                if col == 0:
                    if dest_list[2] != map_matrix[0][0]:
                        map_matrix.append([])
                    else:
                        keepon = False
                        break
                map_matrix[row + 1].append(dest_list[2])
            if dest_list[1] != '0':
                if dest_list[1] != map_matrix[row][0]:
                    if row == 0:
                        map_matrix[row].append(dest_list[1])
                    startingpoint = dest_list[1]
                    col = col + 1
                else:
                    row = row + 1
                    col = 0
                    startingpoint = map_matrix[row][col]
            else:
                if dest_list[2] == '0':
                    keepon = False
                    break
                else:
                    row = row + 1
                    col = 0
                    startingpoint = map_matrix[row][col]
    return map_matrix


def write_bitmap(outdir, data, upperleft, height, width, prefix, map_matrix):
    BUFSIZE = 8*1024
    color_pallette = {'ocean': (0x00, 0xff, 0xff, 0xff),
                      'plain': (0x90, 0xee, 0x90, 0xff),
                      'forest': (0x32, 0xcd, 0x32, 0xff),
                      'swamp': (0xff, 0x00, 0xff, 0xff),
                      'mountain': (0x80, 0x80, 0x80, 0xff),
                      'desert': (0xff, 0xff, 0x00, 0xff),
                      'underground': (0xff, 0xa5, 0x00, 0xff),
                      'cloud': (0xad, 0xd8, 0xe6, 0xff)}
    outf = open(pathlib.Path(outdir).joinpath(prefix + '_thumbnail.png'), 'wb')
    map = PNGCanvas(width, height, color=(0xff, 0, 0, 0xff))
    for x in range(0, width):
        for y in range(0, height):
            try:
                province_box = data[map_matrix[y][x]]
                try:
                    color = color_pallette[u.return_type(province_box)]
                    map.point(x, y, color)
                except KeyError:
                    print('missing color for: {}'.format(u.return_type(province_box)))
            except KeyError:
                # print('missing box record for: {} {}'.format(curr_loc,
                #                                              to_oid(curr_loc)))
                pass
    outf.write(map.dump())
    outf.close()


def write_top_map(outdir, upperleft, height, width, prefix, map_matrix):
    outf = open(pathlib.Path(outdir).joinpath(prefix + '_map.html'), 'w')
    outf.write('<HTML>\n')
    outf.write('<HEAD>\n')
    outf.write('<TITLE>{} Map</TITLE>\n'.format(prefix.capitalize()))
    outf.write('<link href="map.css" rel="stylesheet" type="text/css">\n')
    outf.write('</HEAD>\n')
    outf.write('<BODY>\n')
    outf.write('<h3>Olympia {} Map</h3>\n'.format(prefix.capitalize()))
    if height <= 50 and width <= 50:
        multiple = 12
    elif height <= 80 and width <= 80:
        multiple = 7
    else:
        multiple = 5
    rem_height = height % 10
    if rem_height > 0 and height >= 10:
        iheight = (multiple * (height - 10)) + (rem_height * multiple)
    else:
        iheight = (multiple * height)
    rem_width = width % 10
    if rem_width > 0 and width >= 10:
        iwidth = (multiple * (width - 10)) + (rem_width * multiple)
    else:
        iwidth = (multiple * width)
    outf.write('<img height="{}" width="{}" src="{}_thumbnail.png" usemap="#oly"/>\n'.format(iheight,
                                                                                             iwidth,
                                                                                             prefix))
    outf.write('<map name="oly" id="oly">\n')
    x_max = math.ceil(width / 10)
    y_max = math.ceil(height / 10)
    if x_max == 1:
        lwidth = width * multiple
    else:
        lwidth = int(iwidth / (x_max - 1))
    if y_max == 1:
        lheight = height * multiple
    else:
        lheight = int(iheight / (y_max - 1))
    tp = 0
    bt = lheight
    for outery in range(0, y_max):
        if outery < y_max - 1 or (outery == y_max - 1 and rem_height > 0) or y_max == 1:
            lt = 0
            rt = lwidth
            if outery == 0:
                lt = 0
            elif outery == 1:
                tp = lheight
                bt = bt + lheight
            elif outery == y_max - 2:
                tp = tp + lheight
                bt = bt + lheight
            elif outery == y_max - 1:
                bt = bt + (rem_height * multiple)
            else:
                tp = tp + lheight
                bt = bt + lheight
            for outerx in range(0, x_max):
                if outerx < x_max - 1 or (outerx == x_max - 1 and rem_width > 0) or x_max == 1:
                    if outerx == 0 and x_max != 1:
                        pass
                    elif outerx == 1:
                        lt = lwidth
                        rt = rt + lwidth
                    elif outerx == x_max - 2:
                        lt = lt + lwidth
                        rt = rt + lwidth
                    elif outerx == x_max - 1 or x_max == 1:
                        rt = rt + (rem_width * multiple)
                    else:
                        lt = lt + lwidth
                        rt = rt + lwidth
                    xx = outerx * 10
                    yy = outery * 10
                    currentpoint = map_matrix[yy][xx]
                    outf.write('<area shape="rect" '
                               'coords="{}, {}, {}, {}" href="{}_map_leaf_{}.html"/>\n'.format(lt,
                                                                                               tp,
                                                                                               rt,
                                                                                               bt,
                                                                                               prefix,
                                                                                               to_oid(currentpoint)))
    outf.write('</map>\n')
    outf.write('</BODY>\n')
    outf.write('</html>\n')
    outf.close()


def write_map_leaves(data, castle_chain, outdir, upperleft, height, width, prefix, instance, map_matrix):
    x_max = math.ceil(width / 10)
    y_max = math.ceil(height / 10)
    rem_height = height % 20
    rem_width = width % 20
    for outery in range(0, y_max):
        if outery < y_max - 1 or y_max == 1:
            for outerx in range(0, x_max):
                if outerx < x_max - 1 or x_max == 1:
                    xx = outerx * 10
                    yy = outery * 10
                    currentpoint = map_matrix[yy][xx]
                    printpoint = currentpoint
                    # print('leaf {} ({})'.format(u.to_oid(printpoint),
                    #                             prefix))
                    outf = open(pathlib.Path(outdir).joinpath(prefix +
                                                              '_map_leaf_'
                                                              + u.to_oid(printpoint) +
                                                              '.html'), 'w')
                    maps.write_leaf_header(printpoint, outdir, prefix, outf)
                    outf.write('<TABLE>\n')
                    topnav = False
                    botnav = False
                    leftnav = False
                    rightnav = False
                    upperleftnav = False
                    upperrightnav = False
                    lowerleftnav = False
                    lowerrightnav = False
                    if yy > 9 and height > 20:
                        topnav = True
                    if (height - yy) > 20 and height > 20:
                        botnav = True
                    if xx > 9 and width > 20:
                        leftnav = True
                        if topnav:
                            upperleftnav = True
                        if botnav:
                            lowerleftnav = True
                    if (width - xx) > 20 and width > 20:
                        rightnav = True
                    if rightnav:
                        if topnav:
                            upperrightnav = True
                        if botnav:
                            lowerrightnav = True
                    if topnav:
                        generate_topnav(currentpoint, outf, prefix,
                                        upperleftnav, upperrightnav, xx, yy, map_matrix)
                    for y in range(0, 20):
                        if yy + y < height:
                            outf.write('<tr>\n')
                            for x in range(0, 20):
                                if xx + x < width:
                                    write_cell(castle_chain,
                                               currentpoint,
                                               data,
                                               leftnav,
                                               outf,
                                               prefix,
                                               rightnav,
                                               x,
                                               y,
                                               xx,
                                               yy,
                                               instance,
                                               map_matrix)
                            outf.write('</tr>\n')
                    if botnav:
                        generate_botnav(currentpoint, lowerleftnav,
                                        lowerrightnav, outf, prefix, xx, yy, map_matrix)
                    outf.write('</TABLE>\n')
                    outf.write('<a href="{}_map.html">Return to {} Map</a>'.format(prefix,
                                                                                   prefix.capitalize()))
                    outf.write('</BODY>\n')
                    outf.write('</HTML>')
                    outf.close()


def write_cell(castle_chain, currentpoint, data, leftnav, outf, prefix, rightnav, x, y, xx, yy, instance, map_matrix):
    if x == 0 and y == 0:
        if leftnav:
            printpoint = map_matrix[yy][xx - 10]
            outf.write('<td rowspan="20" class="left">')
            outf.write('<a href="{}_map_leaf_{}.html">'.format(prefix,
                                                               to_oid(printpoint)))
            outf.write('<img src="grey.gif" width="20" height="840">')
            outf.write('</a></td>\n')
    cell = map_matrix[yy+y][xx+x]
    printpoint = cell
    try:
        loc_rec = data[str(printpoint)]
        outf.write('<td id ="{}" class="{}"'.format(to_oid(printpoint),
                                                    u.return_type(loc_rec)))
        maps.generate_border(data, loc_rec, outf, instance)
        outf.write('>')
        maps.generate_cell_contents(castle_chain, printpoint, data, loc_rec, outf)
        outf.write('</td>\n')
    except:
        outf.write('<td id ="{}" class="{}">'.format(to_oid(printpoint),
                                                     'undefined'))
        outf.write('{}'.format(to_oid(printpoint)))
        outf.write('<br>{}'.format('&nbsp;' * 8))
        outf.write('<br>{}'.format('&nbsp;' * 8))
        outf.write('</td>\n')
    # except KeyError:
    #    outf.write('<td id="{}" class="x-sea">{}</td>\n'.format(to_oid(printpoint), to_oid(printpoint)))
    if x == 19 and y == 0:
        if rightnav:
            printpoint = map_matrix[yy][xx + 10]
            outf.write('<td rowspan="20" class="right">')
            outf.write('<a href="{}_map_leaf_{}.html">'.format(prefix,
                                                               to_oid(printpoint)))
            outf.write('<img src="grey.gif" width="20" height="840">')
            outf.write('</a></td>\n')


def generate_botnav(currentpoint, lowerleftnav, lowerrightnav, outf, prefix, xx, yy, map_matrix):
    outf.write('<tr>\n')
    if lowerleftnav:
        printpoint = map_matrix[yy + 10][xx - 10]
        outf.write('<td class="corner">')
        outf.write('<a href="{}_map_leaf_{}.html">'.format(prefix,
                                                           to_oid(printpoint)))
        outf.write('<img src="grey.gif" width="20" height="20">')
        outf.write('</a></td>\n')
    printpoint = map_matrix[yy + 10][xx]
    outf.write('<td colspan="20" class="bottom">')
    outf.write('<a href="{}_map_leaf_{}.html">'.format(prefix,
                                                       to_oid(printpoint)))
    outf.write('<img src="grey.gif" width="840" height="20">')
    outf.write('</a></td>\n')
    if lowerrightnav:
        printpoint = map_matrix[yy + 10][xx + 10]
        outf.write('<td class="corner">')
        outf.write('<a href="{}_map_leaf_{}.html">'.format(prefix,
                                                           to_oid(printpoint)))
        outf.write('<img src="grey.gif" width="20" height="20">')
        outf.write('</a></td>\n')
    outf.write('</tr>\n')


def generate_topnav(currentpoint, outf, prefix, upperleftnav, upperrightnav, xx, yy, map_matrix):
    outf.write('<tr>\n')
    if upperleftnav:
        outf.write('<td class="corner">')
        printpoint = map_matrix[yy - 10][xx - 10]
        outf.write('<a href="{}_map_leaf_{}.html">'.format(prefix,
                                                           to_oid(printpoint)))
        outf.write('<img src="grey.gif" width="20" height="20">')
        outf.write('</a></td>\n')
    outf.write('<td colspan="20" class="top">')
    printpoint = map_matrix[yy - 10][xx]
    outf.write('<a href="{}_map_leaf_{}.html">'.format(prefix,
                                                       to_oid(printpoint)))
    outf.write('<img src="grey.gif" width="840" height="20">')
    outf.write('</a></td>\n')
    if upperrightnav:
        outf.write('<td class="corner">')
        printpoint = map_matrix[yy - 10][xx + 10]
        outf.write('<a href="{}_map_leaf_{}.html">'.format(prefix,
                                                           to_oid(printpoint)))
        outf.write('<img src="grey.gif" width="20" height="20">')
        outf.write('</a></td>\n')
    outf.write('</tr>\n')
