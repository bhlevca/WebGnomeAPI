"""
    Main entry point
"""
import logging
logging.basicConfig()

from pyramid.config import Configurator


def main(global_config, **settings):
    config = Configurator(settings=settings)

    config.add_tween("webgnome_api.tweens.PyGnomeSchemaTweenFactory")
    config.scan("webgnome_api.views")

    return config.make_wsgi_app()
