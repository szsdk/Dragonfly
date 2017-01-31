#!/usr/bin/env python

'''
Convert h5 files generated by Chuck for the SPI
These files have also been classified into singles so no selection file is
needed.

Needs:
    <h5_fname> - Path to photon-converted h5 file used in SPI

Produces:
    EMC file with all the single hits in the h5 file
'''

import os
import numpy as np
import h5py
import sys
import logging
#Add utils directory to pythonpath
sys.path.append(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))
from py_src import py_utils
from py_src import writeemc
from py_src import read_config

if __name__ == '__main__':
    logging.basicConfig(filename='recon.log', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    parser      = py_utils.my_argparser(description='h5toemc')
    parser.add_argument('h5_name', help='HDF5 file to convert to emc format')
    parser.add_argument('-d', '--dset_name', help='Name of HDF5 dataset containing photon data', default=None)
    parser.add_argument('-s', '--sel_file', help='Path to text file containing indices of frames or a set of 0 or 1 values. Default: Do all', default=None)
    parser.add_argument('-S', '--sel_dset', help='Same as --sel_file, but pointing to the name of an HDF5 dataset', default=None)
    parser.add_argument('-l', '--list', help='h5_name is list of h5 files rather than a single one', action='store_true', default=False)
    args        = parser.special_parse_args()

    logging.info('Starting h5toemc_spi2....')
    logging.info(' '.join(sys.argv))
    pm          = read_config.get_detector_config(args.config_file, show=args.vb)
    output_folder = read_config.get_filename(args.config_file, 'emc', 'output_folder')

    if not os.path.isfile(args.h5_name):
        print 'Data file %s not found. Exiting.' % args.h5_name
        logging.error('Data file %s not found. Exiting.' % args.h5_name)
        sys.exit()

    if args.list:
        logging.info('Reading file names in list %s' % args.h5_name)
        with open(args.h5_name, 'r') as f:
            flist = [fname.rstrip() for fname in f.readlines()]
        logging.info
    else:
        flist = [args.h5_name]

    emcwriter = writeemc.EMC_writer('%s/%s.emc' % (output_folder, os.path.splitext(os.path.basename(args.h5_name))[0]),
                                    pm['dets_x']*pm['dets_y'])

    for fname in flist:
        f = h5py.File(fname, 'r')
        if args.dset_name is None:
            for name, obj in f['photonConverter'].items():
                try:
                    temp = obj.keys()
                    dset = obj['photonCount']
                    break
                except AttributeError:
                    pass
            logging.info('Converting data in '+ dset.name)
        else:
            dset = f[args.dset_name]
            logging.info('Converting data in '+ args.dset_name)

        if args.sel_file is not None and args.sel_dset is not None:
            logging.info('Both sel_file and sel_dset specified. Pick one.')
            sys.exit(1)
        elif args.sel_file is None and args.sel_dset is None:
            ind = np.arange(dset.shape[0], dtype='i4')
        elif args.sel_file is not None:
            ind = np.loadtxt(args.sel_file, dtype='i4')
        else:
            ind = f[args.sel_dset][:]

        if ind.shape[0] == dset.shape[0] and ind.max() < 2:
            ind = np.where(ind==1)[0]

        num_frames = ind.shape[0]
        if not args.list:
            logging.info('Converting %d/%d frames in %s' % (num_frames, dset.shape[0], args.h5_name))

        for i in range(num_frames):
            photons = dset[ind[i]]
            photons[photons<0] = 0
            emcwriter.write_frame(photons.flatten())
            if not args.list:
                sys.stderr.write('\rFinished %d/%d' % (i+1, num_frames))

        f.close()

    if not args.list:
        sys.stderr.write('\n')
    emcwriter.finish_write()