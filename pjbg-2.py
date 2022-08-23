#!/usr/bin/env python3

# Paul E. Johnson <pauljohn@ku.edu>
# 20150102

# A script to randomly reassign compiz background images for viewports.
# Recall compiz after 0.9.2 uses "viewports" to simulate workspaces.

# Will choose an image file randomly from within dir hierarchy.

# Can replace one viewport's wallpaper.  The w argument will be
# interpreted in one of 3 ways
# 
# 1. If w is either 0 or -1, this means remove all
# existing wallpapers and replace with one randomly chosen image.
#
# 2. If w is -2, then all workspace backgrounds will be replaced
# with different images from same directory
#
# 3. If 1 <= w <= N (where there are N wallpaper images already
# defined), then the image on viewport w will be replaced. All of the
# other images will remain the same.
#
# 4. If N < w, we interpret this as a request to expand the
# wallpaper array by one.
# 

# I thought it was a little interesting to make types 1 and 3
# work together with compiz. To change the number of wallpapers,
# it is required to correctly change these variables in the
# wallpaper plugin as well:
# "bg-fill-type"
# "bg-image-pos"
# "bg-color1", 
# "bg-color2", 

# I had previously been doing this by dbus-send, but compiz's
# interaction with dbus has become less and less stable, so this version
# uses "gsettings".

# About the schema argument:
# Because I do not use Unity as my desktop environment, I have to point
# SCHEMA at the location where compiz stores wallpapers. If you get
# compiz working with XFCE4, for example, make sure you use the Gsettings
# backend and DO allow Compiz to interact with the desktop environment in
# advanced settings. 

# If you are using Unity, you probably need to change the path, removing
# "Default" with "unity".  You can do from command line or by editing script.

# If you want to know how to get Compiz going without the Unity Desktop, 
# this is not a bad set of advice 
# http://www.webupd8.org/2012/11/how-to-set-up-compiz-in-xubuntu-1210-or.html
# If you have Unity installed, it is necessary to remove it, or else
# launching compiz with the Gsettings back end gets Ubuntu all confused and
# Unity keeps starting at same time. If you have trouble with that, I can help


import argparse
import subprocess
# import sys
import os
import random

parser = argparse.ArgumentParser()

parser.add_argument("-d", "--dir", help="directory path",
                    default="/usr/local/share/Backgrounds")
parser.add_argument("-p", "--pages", help="pages", default="1", type=int)
parser.add_argument("-w", "--workspace", 
                    help="workspace number, -1,  0, 1-n, or > n", default="0", 
                    type=int)
parser.add_argument("-f", "--fff", help="a dummy argument to fool ipython", default="1")
parser.add_argument("-schema", help="gsettings shema", 
                    metavar="SCHEMA",
                    default="org.compiz.wallpaper:/org/compiz/profiles/Default/plugins/wallpaper/")
parser.add_argument("-key", help = "gsettings key", metavar = "KEY", default = "bg-image")
args = parser.parse_args()

process_output = subprocess.check_output(["gsettings", "get", args.schema, args.key]) 

## previus will be an arra with markup like b"['/tmp...]"
array = eval(process_output)

print("Original array\n")
print(array)
print("Original array end\n")
arraylen = len(array)

# python arrays index 0, ... , N-1, so downshift workspace number
ws = args.workspace - 1



## See https://stackoverflow.com/questions/30897800/python-non-repeating-random-values-from-list
def generate_random(my_list, number_of_choices):
    chosen = []
    cnt = 0
    while cnt < number_of_choices:
        try:
            choice = random.choice(my_list)
        except:
            breakpoint()
        if choice not in chosen:
            chosen.append(choice)
            cnt +=1
    return chosen




def getFn(pages, mydir, myws):
    if pages > 1:
        dirlist = [os.path.join(dp, f) for dp, dn, fn in
                   os.walk(os.path.expanduser(mydir)) for f in dn]
        if (len(dirlist) > 0):
            filelist = [os.path.join(dp, f) for dp, dn, fn in
                        os.walk(os.path.expanduser(random.choice(dirlist))) for f in fn]
        else:
            filelist = [os.path.join(dp, f) for dp, dn, fn in
                        os.walk(os.path.expanduser(mydir)) for f in fn]
        ##print(filelist)
        ##filename1 = random.choice(filelist)
        ##filename2 = random.choice(filelist)
        filenames = generate_random(filelist, 2)
        print(filenames)
        newfn = '/tmp/dual-%d.jpg' % myws
        if (os.path.isfile(newfn)) is True:
            os.remove(newfn)
            newfn = '/tmp/dual-%d.%s.jpg' % (myws, "2")
        subprocess.call(["montage", filenames[0], filenames[1],
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




# print("Array length was")
# print(arraylen)

# If ws 0 or smaller, we are going to reset whole collection back to
# just one image. if ws > N of images, then add a new image.
if ws == -3:
    for num in range(len(array)):
        array[num] = getFn(args.pages, args.dir, num)
    print(array)

    subprocess.call(["gsettings", "set", args.schema, args.key, str(array)])
elif ws < 0:
    filename = getFn(args.pages, args.dir, 1)
    array = [str(filename)]
    subprocess.call(["gsettings", "set", args.schema, args.key, str(array)])
    subprocess.call(["gsettings", "set", args.schema,
                     "bg-fill-type", str("[0]")])
    subprocess.call(["gsettings", "set", args.schema,
                     "bg-image-pos", str("[0]")])
    subprocess.call(["gsettings", "set", args.schema,
                     "bg-color1", str("['#000000ff']")])
    subprocess.call(["gsettings", "set", args.schema,
                     "bg-color2", str("['#000000ff']")])
elif ws < arraylen:
    filename = getFn(args.pages, args.dir, ws)
    array[ws]=str(filename)
    subprocess.call(["gsettings", "set", args.schema, args.key, str(array)])
else:
    filename = getFn(args.pages, args.dir, len(array))
    array.append(str(filename))
    subprocess.call(["gsettings", "set", args.schema, args.key, str(array)])
    arraylen = len(array)
    subprocess.call(["gsettings", "set", args.schema,
                     "bg-fill-type", str([0]*arraylen)])
    subprocess.call(["gsettings", "set", args.schema,
                     "bg-image-pos", str([0]*arraylen)])
    subprocess.call(["gsettings", "set", args.schema,
                     "bg-color1", str(['#000000ff']*arraylen)])
    subprocess.call(["gsettings", "set", args.schema,
                     "bg-color2", str(['#000000ff']*arraylen)])

subprocess.call(["gsettings", "set", args.schema, args.key, str(array)])

print("HELLO, corrected image array is:")
print('\n '.join(array))
