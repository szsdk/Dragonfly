#!/usr/bin/env python
import os
import sys
import shutil
import argparse
import ConfigParser
sys.path.append(os.path.join(os.path.dirname(sys.argv[0]), "utils"))
from py_src import py_utils

if __name__ == "__main__":
    parser = argparse.ArgumentParser("Creates new reconstruction instance based on template in this folder")
    parser.add_argument("-t", "--recon_file_tag", dest="recon_tag", default="recon",
                        help="prefixes the reconstruction folders with your specified tags.")
    parser.add_argument("-r", "--recon_run_num", dest="run_tag", type=int, default=1,
                        help="give your reconstruction a specific number")
    parser.add_argument("-p", "--recon_prefix", dest="recon_prefix", default="./",
                        help="path to the folder containing the reconstruction folder")
    parser.add_argument("-l", "--link_to_parent_data", dest="link_to_parent_data", action="store_true",
                        default=False,
                        help="link data generated by your reconstruction into the parent directory")
    parser.add_argument("--exp", dest="exp", default=False, action="store_true",
                        help="use if processing experimental data")
    args = parser.parse_args()
    args.recon_prefix = os.path.realpath(args.recon_prefix)

    curr_dir = os.getcwd()
    parent_dir = os.path.dirname(os.path.realpath(sys.argv[0]))
    new_recon_dir = py_utils.create_new_recon_dir(tag=args.recon_tag, num=args.run_tag, prefix=args.recon_prefix)

    print 80*"="
    print "Initializing new directory and creating soft links to useful utilities."
    print "Type './init_new_recon.py -h' for options"
    print "See http://github.com/duaneloh/Dragonfly/wiki/FAQ for troubleshooting tips."
    print "Feel free to email Kartik Ayyer <kartik.ayyer@desy.de>"
    print "or Duane Loh <duaneloh@nus.edu.sg> if the FAQ does not help."
    print 80*"="

    if args.recon_prefix != './':
        print "Created new directory:", new_recon_dir

    if args.link_to_parent_data:
        try:
            os.symlink(os.path.join(curr_dir, new_recon_dir,"data"), os.path.join("data", new_recon_dir))
        except:
            print "Failed to create following symlink"
            print os.path.join("data", new_recon_dir), "-->", os.path.join(curr_dir, new_recon_dir,"data")
            print "Reconstructions not affected.."

    os.chdir(curr_dir)
    os.chdir(parent_dir)
    os.system("make")
    (relD, ln_dirs,) = (parent_dir, ["aux", "emc"])
    (relC, copies,) = (parent_dir, ["config.ini"])
    if not args.exp:
        (relU, ln_utils,) = (os.path.join(parent_dir, "utils"), ["make_detector.py",
                                                             "make_densities.py",
                                                             "make_intensities.py",
                                                             "make_data",
                                                             "run_emc.py",
                                                             "sim_setup.py",
                                                             "autoplot.py",
                                                             "frameviewer.py",
                                                             "powder.py", 
                                                             "convert"])
    else:
        (relU, ln_utils,) = (os.path.join(parent_dir, "utils"), ["make_detector.py",
                                                             "run_emc.py",
                                                             "autoplot.py",
                                                             "frameviewer.py",
                                                             "powder.py", 
                                                             "classifier.py",
                                                             "convert"])

    os.chdir(new_recon_dir)
    for ld in ln_dirs:
        src = os.path.join(relD, ld)
        os.symlink(src, ld)
    for lu in ln_utils:
        src = os.path.join(relU, lu)
        os.symlink(src, lu)
    for lc in copies:
        src = os.path.join(relC, lc)
        shutil.copy(src, lc)

    os.chdir(curr_dir)
