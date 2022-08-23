#!/usr/bin/env python3

"""
Paul E. Johnson <pauljohn@ku.edu>
20160331

A Python script to randomly reassign background images for xfce.

Command line arguments give the number of the workspace to change,
the directory from which to randomly choose an image,
and the number of pages "wide" the image should be.

Example usages:


$ ./bgsetter.py -w6 -d "/usr/local/share/Backgrounds/Water"


That uses defaults p=1 and device=LVDS, which on my laptop
is the display screen. Alternate devices I encounter regularly are
VGA and HDMI.

If you use p=2, it will help on a double monitor setup. If pages = 2,
then ImageMagick montage will create a wide background image that
can stretch across 2 pages.  Can replace one viewport's wallpaper.
The w argument will be interpreted in one of 3 ways # # In previous
versions of this, for the compiz desktop, # there were fancy settings
to reset all workspace viewports at # once. I've not implemented that
here.
"""

import argparse
import subprocess
import os
import random

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("-d", "--dir", help="directory path",
                    default="/usr/local/share/Backgrounds", dest="dir")
parser.add_argument("-p", "--pages", help="pages", default="1",
                    type=int, dest="pages")
parser.add_argument("-w", "--workspace", help="workspace number, integer",
                    default="1", dest="w", type=int)
parser.add_argument("-v", "--device", help="device name LVDS, HDMI, or VGA",
                    default="LVDS", dest="device", type=str)
parser.add_argument("-z", "--zoom", help="image zoom: 2:tiled 3:stretched 4:scaled 5:zoom 6:span",
                    default="5", dest="zoom", type=str)


args = parser.parse_args()
print(args)

# A workspace number 1 will be internally referred to as 0
# in the XFCE window manager
ws = str(args.w - 1)

def getFn(pages, mydir, myws):
    """ Randomly choose an image file within mydir.
    """
    if pages > 1:
        dirlist = [os.path.join(dp, f) for dp, dn, fn in
                   os.walk(os.path.expanduser(mydir)) for f in dn]
        if (len(dirlist) > 0):
            filelist = [os.path.join(dp, f) for dp, dn, fn in
                        os.walk(os.path.expanduser(random.choice(dirlist))) for f in fn]
        else:
            filelist = [os.path.join(dp, f) for dp, dn, fn in
                        os.walk(os.path.expanduser(mydir)) for f in fn]
        # print(filelist)
        filename1 = random.choice(filelist)
        filename2 = random.choice(filelist)
        newfn = '/tmp/dual-%d.jpg' % myws
        if (os.path.isfile(newfn)) is True:
            os.remove(newfn)
            newfn = '/tmp/dual-%d.%s.jpg' % (myws, "2")
        subprocess.call(["montage", filename1, filename2,
                         "-tile",  "2x1", "-geometry", "1600x1200+0+0",
                         "-background", "black", newfn])
        filename = newfn
    else:
        filename = random.choice([os.path.join(dp, f) for dp, dn,
                                  fn in os.walk(os.path.expanduser(mydir))
                                  for f in fn])
    print("The newly found filename is:")
    print(filename)
    return(filename)


print(args.pages)
print("args.dir" + args.dir)

filename = getFn(args.pages, args.dir, ws)

cmd1 = ['xfconf-query', '-c', 'xfce4-desktop', '-p',
       "".join(['/backdrop/screen0/monitor', str(args.device),
                '/workspace', ws ,'/last-image']),
       '-s',  filename]
print(" ".join(cmd1))

subprocess.call(cmd1)

# image-style 0:none 1:centered2:tiled 3:stretched 4:scaled 5:zoomed 
cmd2 = ['xfconf-query', '-c', 'xfce4-desktop', '-p',
        "".join(['/backdrop/screen0/monitor', str(args.device),
                 '/workspace', ws, '/image-style']),
        '-s', args.zoom]
subprocess.call(cmd2)

# Why doesn't this work? Manuals say it ougth to:
#process = subprocess.Popen(cmd1, shell=True, stdout=subprocess.PIPE)
#process.wait()
#print(process.returncode)


# Tips on interacting with xfconf-query
# xfconf-query -c xfce4-desktop -p /backdrop -l
# xfconf-query --channel xfce4-desktop --list
# Basic syntax to change background on LVDS1 device, workspace 3
#xfconf-query -c xfce4-desktop -p /backdrop/screen0/monitorLVDS1/workspace3/last-image -s /usr/local/share/Backgrounds/Water/Sozaijiten.Vol40-Seas+SouthIslands-Vol_040_AQ182.jpg

# xfconf-query -c xfce4-desktop -p
#"/backdrop/screen0/monitor0/image-style" -s "0"
# (0 for "auto", 1 for "centered", etc.)
