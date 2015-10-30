import os
import shutil
import stat
import subprocess
import numpy as np

from sklearn.metrics import euclidean_distances
from sklearn.isotonic import IsotonicRegression

from .config import parse
from .optimization import MDS, PM1, PM2


max_iter = 5

CMD_PM = ('%s -o %s -w 8 '
          '-r %d '
          '-k %s '
          '-i %s '
          '-d %f '
          '-c %s -y 1 -a %f -b %f > %s')


CMD_MDS = ('%s -o %s -w 8 '
           '-r %d '
           '-k %s '
           '-i %s '
           '-d %s '
           '-c %s -y 1 > %s')


def run_mds(directory):

    if os.path.exists(os.path.join(directory,
                                   "config.ini")):
        config_file = os.path.join(directory, "config.ini")
    else:
        config_file = None

    options = parse(config_file)

    random_state = np.random.RandomState(seed=options["seed"])

    # First, compute MDS
    counts = np.load(os.path.join(directory,
                                  options["counts"]))
    mds = MDS(alpha=options["alpha"],
              beta=options["beta"],
              random_state=random_state,
              max_iter=options["max_iter"],
              verbose=options["verbose"])
    X = mds.fit(counts)
    np.savetxt(
        os.path.join(
            directory,
            "MDS." + options["output_name"]),
        X)

    return True


def run_nmds(directory):

    if os.path.exists(os.path.join(directory,
                                   "config.ini")):
        config_file = os.path.join(directory, "config.ini")
    else:
        config_file = None

    options = parse(config_file)
    run_mds(directory)

    for i in range(0, max_iter):
        if i == 0:
            try:
                X = np.loadtxt(
                    os.path.join(directory,
                                 "MDS." + options["output_name"] + ".txt"))
            except IOError:
                return
        else:
            X = np.loadtxt(
                os.path.join(directory,
                             '%d.NMDS.' % (i) + options["output_name"] +
                             ".txt"))

        X = X.reshape((len(X) / 3, 3))

        dis = euclidean_distances(X) * 1000
        counts = np.load(
            os.path.join(directory, options["counts"]))
        counts[np.isnan(counts)] = 0

        wish_distances = np.zeros(counts.shape)

        print "Fitting isotonic regression..."
        ir = IsotonicRegression()
        wish_distances[counts != 0] = ir.fit_transform(
            1. / counts[counts != 0],
            dis[counts != 0])
        print "writing wish distances"

        lengths = np.loadtxt(
            os.path.join(directory, options["organism_structure"]))

        try:
            len(lengths)
        except TypeError:
            lengths = np.array([lengths])

        write(wish_distances,
              os.path.join(directory,
                           '%d.NMDS.wish_distances.txt' % i),
              lengths=lengths, resolution=options["resolution"])

        if i == 0:
            shutil.copy(
                os.path.join(directory,
                             "MDS." + options["output_name"] + ".txt"),
                os.path.join(directory,
                             '%d.NMDS.' % (i + 1) + options["output_name"] +
                             ".temp.txt"))
        else:
            shutil.copy(
                os.path.join(directory,
                             '%d.NMDS.' % i + options["output_name"] + ".txt"),
                os.path.join(directory,
                             '%d.NMDS.' % (i + 1) + options["output_name"] +
                             ".temp.txt"))

        cmd = CMD_MDS % (options["binary_mds"],
                         os.path.join(directory,
                                      "%d.NMDS." % (i + 1) +
                                      options["output_name"]),
                         options["resolution"],
                         os.path.join(directory,
                                      options["organism_structure"]),
                         os.path.join(directory,
                                      "%d.NMDS.wish_distances.txt" % (i)),
                         options["adjacent_beads"],
                         options["chromosomes"],
                         os.path.join(directory,
                                      str(i + 1) + '.NMDS.log'))

        filename = os.path.join(directory, str(i + 1) + '.NMDS.sh')
        fileptr = open(filename, 'wb')
        fileptr.write(cmd)
        fileptr.close()
        st = os.stat(filename)
        os.chmod(filename, st.st_mode | stat.S_IXUSR)
        subprocess.call(filename.split(), shell='True')


def run_pm1(directory):
    if os.path.exists(os.path.join(directory,
                                   "config.ini")):
        config_file = os.path.join(directory, "config.ini")
    else:
        config_file = None

    options = parse(config_file)

    random_state = np.random.RandomState(seed=options["seed"])

    options = parse(config_file)
    counts = np.load(os.path.join(directory, options["counts"]))
    pm1 = PM1(alpha=options["alpha"],
              beta=options["beta"],
              random_state=random_state,
              max_iter=options["max_iter"],
              verbose=options["verbose"])
    X = pm1.fit(counts)
    np.savetxt(
        os.path.join(
            directory,
            "PM1." + options["output_name"]),
        X)

    return True


def run_pm2(directory):
    if os.path.exists(os.path.join(directory,
                                   "config.ini")):
        config_file = os.path.join(directory, "config.ini")
    else:
        config_file = None

    options = parse(config_file)

    random_state = np.random.RandomState(seed=options["seed"])

    options = parse(config_file)
    counts = np.load(os.path.join(directory, options["counts"]))
    pm2 = PM2(alpha=options["alpha"],
              beta=options["beta"],
              random_state=random_state,
              max_iter=options["max_iter"],
              verbose=options["verbose"])
    X = pm2.fit(counts)
    np.savetxt(
        os.path.join(
            directory,
            "PM2." + options["output_name"]),
        X)
    return True
