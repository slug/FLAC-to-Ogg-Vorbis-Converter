#!/usr/bin/python
#
# Copyright (c) 2010-Eternity Gerald Gold and Channelping.
# All rights reserved. This program is free software; you
# may redistribute it and/or modify it under the same terms
# as Python itself.
#
# http://channelping.com/audio/
#---------------------------------------------------------------------

from pprint import pprint
import os
import sys
import re
import glob
import optparse

# system command functionality
from subprocess import Popen
from subprocess import call
from subprocess import PIPE

# get meta data from flac file
from mutagen.flac import FLAC

# write meta data to ogg file
import tagpy

DEFAULT_ENCODING = 'utf-8'
PROGRAM_VERSION = '1.1'

def create_ogg_vorbis(comments, file, bitrate):

    print "converting to ogg: [%s]\n" % file

    # Depending on how tags were originally written to input flac
    # file, keys are either all uppercase or all lowercase.
    if comments.has_key('TITLE'):
        artist = str(comments.get('ARTIST',      ''))
        album  = str(comments.get('ALBUM',       ''))
        title  = str(comments.get('TITLE',       ''))
        trkno  = str(comments.get('TRACKNUMBER', '')).rjust(2, '0')
        date   = str(comments.get('DATE',        ''))
        genre  = str(comments.get('GENRE',       ''))
    else:
        artist = str(comments.get('artist',      ''))
        album  = str(comments.get('album',       ''))
        title  = str(comments.get('title',       ''))
        trkno  = str(comments.get('tracknumber', '')).rjust(2, '0')
        date   = str(comments.get('date',        ''))
        genre  = str(comments.get('genre',       ''))

    # these get converted to int later
    date = re.sub('\D', '', date)[:4]
    trkno = re.sub('\D', '', trkno)

    fixed_comments = {}
    fixed_comments['artist'] = artist
    fixed_comments['album']  = album
    fixed_comments['title']  = title
    fixed_comments['trkno']  = trkno
    fixed_comments['date']   = date
    fixed_comments['genre']  = genre

    switches = []
    switches.append('-b %s' % bitrate)

    abs_flac_name = file
    abs_ogg_name  = re.sub('\.flac$', '.ogg', os.path.basename(file))

    flac_to_oggenc_cmd = 'flac -c -d "%s" | oggenc %s - -o "%s" 2>/dev/null' % (abs_flac_name,
                                                                                ' '.join(switches),
                                                                                abs_ogg_name)

    ### print(flac_to_oggenc_cmd); sys.exit(0)

    #---------------------------------------------------------------------
    # Execute system command
    #---------------------------------------------------------------------
    try:
        retcode = call(flac_to_oggenc_cmd, shell=True)
        print("")
        if retcode < 0:
            print >>sys.stderr, "Child was terminated by signal", -retcode
        else:
            print >>sys.stderr, "Child returned", retcode
    except OSError, e:
        print >>sys.stderr, "Execution failed:", e

    #---------------------------------------------------------------------
    # Transfer Meta Data to new .ogg file
    #---------------------------------------------------------------------
    write_ogg_metadata(abs_ogg_name, fixed_comments)
# end create_ogg_vorbis()

def write_ogg_metadata(filename, comments):
    file_obj = tagpy.FileRef(filename)
    tag_obj = file_obj.tag()

    tag_obj.artist = comments['artist'].decode(DEFAULT_ENCODING)
    tag_obj.album  = comments['album'].decode(DEFAULT_ENCODING)
    tag_obj.title  = comments['title'].decode(DEFAULT_ENCODING)
    tag_obj.year   = int(comments['date'].decode(DEFAULT_ENCODING))
    tag_obj.track  = int(comments['trkno'].decode(DEFAULT_ENCODING))
    tag_obj.genre  = comments['genre'].decode(DEFAULT_ENCODING)

    file_obj.save()
# end write_ogg_metadata

def get_options():
    version_info = 'flac2ogg.py: version %s' % (PROGRAM_VERSION)
    p = optparse.OptionParser(version=version_info)

    p.add_option('-d', action='store', dest='flac_dir',
                 help = '''Set full path (with or without trailing slash)
                        to flac directory: $ flac2ogg.py -d /music/bartok/concertos/
                        Current directory is used if -d switch omitted
                        ''')

    p.add_option('-b', action='store', dest='bitrate',
                 help = '''Specify ogg file bitrate encoding: $ flac2ogg.py -b 128
                           Default bitrate is 256 if -b switch omitted'''
                 )

    p.set_defaults(flac_dir='.')
    p.set_defaults(bitrate='256')
    opts, args = p.parse_args()
    return opts
# end get_options

def main():
    # get command line options
    options = get_options()
    bitrate = options.bitrate
    source_dir = re.sub('\/+$', '', options.flac_dir)

    # Process files in directory specified via -d option (not recursive).
    flac_meta = {}
    for file in glob.iglob("%s/*.flac" % source_dir):
        raw_flac_meta = FLAC(file)

        # meta data allows for multiple items per tag key; hence the
        # join()
        flac_meta = {}
        for k, v in raw_flac_meta.items():
            flac_meta[k] = ' '.join(v).encode(DEFAULT_ENCODING, 'replace')    

        create_ogg_vorbis(flac_meta, file, bitrate)
    # end file processing

# end main()

if __name__ == '__main__':
    main()
    sys.exit(0)
