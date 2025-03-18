#!/usr/bin/env bash
source /home/hkcrc/.cache/pypoetry/virtualenvs/mppiisaac-P0pg15jl-py3.8/bin/activate
python /home/hkcrc/mf_code/mppi-isaac/examples/gen3_poly/world.py & python /home/hkcrc/mf_code/mppi-isaac/examples/gen3_poly/planner.py

# TODO fix wrong collision avoidance