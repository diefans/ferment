import click
import docker

from wheezy.template.engine import Engine
from wheezy.template.ext.core import CoreExtension
from wheezy.template.ext.code import CodeExtension
from wheezy.template.loader import DictLoader

from . import templates

import logging

LOG = logging.getLogger(__name__)


LOG_LEVELS = {
    "info": logging.INFO,
    "warn": logging.WARN,
    "debug": logging.DEBUG,
    "error": logging.ERROR,
    "critical": logging.CRITICAL,
}


class Context(dict):
    def __init__(self, *args, **kwargs):
        self.__dict__ = self
        super(Context, self).__init__(*args, **kwargs)


class FermConfig(object):
    def __init__(self, path):
        self.path = path

        template_dct = {
            'docker': templates.docker,
        }
        engine = Engine(
            loader=DictLoader(template_dct),
            extensions=[
                CoreExtension(),
                CodeExtension()
            ]
        )
        self.templates = {
            name: engine.get_template(name) for name in template_dct
        }

    def get_config(self, config):
        return self.templates['docker'].render(config)


@click.group()
@click.option(
    "--log-level",
    type=click.Choice([k for k, v in sorted(LOG_LEVELS.iteritems(), key=lambda x: x[1])]),
    default="info",
    help="Logging level.")
@click.pass_context
def run(ctx, log_level):
    logging.basicConfig(level=LOG_LEVELS[log_level])

    ctx.obj = Context()


@run.group("docker")
@click.option(
    "api", "--docker", "-d",
    type=click.Path(),
    default="unix://var/run/docker.sock",
    help="The docker api socket."
)
@click.option(
    "--cidr", "-c", default="172.18.0.0/16",
    help="Docker CIDR."
)
@click.option(
    "--interface", "-i", default="docker0",
    help="Docker interface."
)
@click.pass_context
def docker_grp(ctx, api, cidr, interface):
    ctx.obj.client = docker.Client(base_url=api)
    ctx.obj.cidr = cidr
    ctx.obj.interface = interface


@docker_grp.command(name="config")
@click.pass_context
def docker_config(ctx):
    ferm = FermConfig(None)

    # get all containers
    containers = ctx.obj.client.containers()

    ctx.obj.containers = [
        ctx.obj.client.inspect_container(container['Id'])
        for container in containers
    ]
    click.echo(ferm.get_config(ctx.obj))
