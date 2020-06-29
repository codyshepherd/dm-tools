import click

from chamber import Chamber

@click.command()
@click.option('-m', '--max-chambers', type=int,
              help="The maximum number of chambers in the dungeon", default=1)
def main(max_chambers):
    ch = Chamber()
    print(ch.shape.type)
    print(ch.render())

if __name__ == '__main__':
    main()
