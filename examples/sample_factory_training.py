
import sys

from sample_factory.algorithms.utils.arguments import arg_parser, parse_args
from sample_factory.envs.env_registry import global_env_registry
from sample_factory.run_algorithm import run_algorithm

from procgen_prims import create_env

#import torch
#torch.multiprocessing.set_start_method('spawn')

def make_env_func(full_env_name, cfg=None, env_config=None):
    port = 56000
    if env_config:
        port += 1 + env_config.env_id

    return create_env(executable="/home/edward/work/simenv/integrations/Unity/builds/simenv_unity.x86_64", port=port, headless=True)


def register_custom_components():
    global_env_registry().register_env(
        env_name_prefix='simenv',
        make_env_func=make_env_func,
    )

def main():
    """Script entry point."""
    register_custom_components()
    parser = arg_parser()
    cfg = parse_args(parser=parser)
    status = run_algorithm(cfg)
    return status


if __name__ == '__main__':
    sys.exit(main())