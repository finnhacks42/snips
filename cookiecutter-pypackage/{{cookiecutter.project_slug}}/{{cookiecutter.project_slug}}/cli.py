"""Console scripts."""

import sys
import click


@click.command()
def say_hello(args=None):
    """Demo console script."""
    click.echo("Hello world")
    click.echo("To make a better script, see click documentation at https://click.palletsprojects.com/")
    return 0

