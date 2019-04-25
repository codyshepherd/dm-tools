#!/usr/bin/env python3
import click
import os
import subprocess
import sys

DEFAULT_DIR = '.'
PANDOC_CMD = 'pandoc --toc {} --pdf-engine=pdflatex ' \
             '-V geometry:margin=1in -o {}.pdf'


@click.command()
@click.option('-t', '--target', type=click.Path(exists=True))
@click.option('-d', '--destination', type=click.Path(exists=True),
              help="The directory you want the finished files written to")
def pandoc(target, destination):

    target_dir = DEFAULT_DIR if target is None else target
    dest_dir = target_dir if destination is None else destination

    files = os.listdir(target_dir)

    if files is None or len(files) == 0:
        print("No files found in target directory.")
        sys.exit(1)

    for f in files:
        print("file: ", f)
        fullpath_target = target_dir + '/' + f
        prefix, file_type = tuple(f.split('.', 2))
        destpath = dest_dir + '/' + prefix
        cmd = PANDOC_CMD.format(fullpath_target, destpath).split(' ')
        print("running the following command:")
        print(' '.join(cmd))
        print(subprocess.check_output(cmd))


if __name__ == '__main__':
    pandoc()
