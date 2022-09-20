import sys

from sample_factory.cfg.arguments import parse_full_cfg, parse_sf_args
from sample_factory.envs.env_utils import register_env
from sample_factory.train import run_rl


from collectables import generate_map
import simenv as sm

"""
To run this example:

git clone git@github.com:alex-petrenko/sample-factory.git
git checkout sf2
cd sample-factory
pip install .

"""


def make_env_func(full_env_name, cfg=None, env_config=None):
    port = 56000
    if env_config:
        port += 1 + env_config.env_id
    env = sm.RLEnv(
        generate_map,
        32,
        16,
        engine_exe="/home/edward/work/simenv/integrations/Unity/builds/simenv_unity.x86_64",
        engine_port=port,
    )
    return env


def register_simenv_components():
    register_env("simenv", make_env_func)


def parse_simenv_args(argv=None, evaluation=False):
    parser, partial_cfg = parse_sf_args(argv=argv, evaluation=evaluation)
    final_cfg = parse_full_cfg(parser, argv)
    return final_cfg


def main():
    """Script entry point."""
    register_simenv_components()
    cfg = parse_simenv_args()

    status = run_rl(cfg)
    return status


if __name__ == "__main__":
    sys.exit(main())
