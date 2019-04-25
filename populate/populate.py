#!/usr/bin/env python3
import click
import os.path as path
import yaml


@click.command()
@click.argument('target', type=click.Path(exists=True))
@click.argument('source-yaml', type=click.Path(exists=True))
@click.option('-d', '--destination', type=click.Path(exists=True),
              help="The directory you want the finished files written to")
def populate(target, source_yaml, destination):
    '''
    This script's purpose is to replace [fill-keys] in the target text
    with the corresponding text from from the source yaml file. It then
    generates n separate files, where n is the number of items in the set
    of all numbers used in all the fill keys in the yaml.

    e.g. if fill-key-1 has items 1 thru 4, and fill-key-2 has item 5, then
    five files will be generated. Fill keys will be replaced based on their
    number; 1s will go with 1s, and so forth.
    '''

    with open(source_yaml, 'r') as fh:
        src = yaml.load(fh)

    with open(target, 'r') as fh:
        dest = fh.read()

    basename = path.basename(target)
    if destination is None:
        directory = path.dirname(target)
    else:
        directory = destination
    prefix, file_type = tuple(basename.split('.', 2))
    filename = prefix + '-{}.' + file_type
    copies = {}
    # Loop over all the fill keys
    for fill_key in src.keys():
        searchstring = '[{}]'.format(fill_key)
        print("Searchstring: ", searchstring)

        if searchstring in dest:
            # Loop over all versions of filler text
            for item in src[fill_key].keys():
                # Copy over original destination material
                if copies.get(item) is None:
                    copies[item] = dest

                print("Item: ", item)
                # Replace the fill key with txt from yaml
                copies[item] = copies[item].replace(searchstring,
                                                    src[fill_key][item])

    # Write out all versions
    for item in copies.keys():
        formatted = filename.format(str(item))
        fullpath = directory + '/' + formatted
        with open(fullpath, 'w+') as fh:
            fh.write(copies[item])

    print("Done.")


if __name__ == '__main__':
    populate()
