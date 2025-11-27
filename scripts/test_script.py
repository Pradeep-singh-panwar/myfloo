#!/usr/bin/env python3
"""

-------------------------------------------------------
Reads a YAML config describing routers/nodes/topology
and generates a synthesizable SystemVerilog NoC fabric.
"""

import os
import sys
import yaml
import argparse
import re
from jinja2 import Template

# =====================================================
# 1. Parse Command Line
# =====================================================
parser = argparse.ArgumentParser(description="FlooNoC RTL Generator")
parser.add_argument("--config", required=True, help="Path to YAML NoC config file")
parser.add_argument("--output", required=True, help="Directory for generated files")
parser.add_argument("--fusesoc", action="store_true", help="Generate FuseSoC .core file")
args = parser.parse_args()

os.makedirs(args.output, exist_ok=True)

# =====================================================
# 2. Load YAML Configuration
# =====================================================
try:
    with open(args.config, "r") as f:
        cfg = yaml.safe_load(f)["noc"]
except Exception as e:
    sys.exit(f"[ERROR] Failed to read config: {e}")

name = cfg.get("name", "noc_generated")
topology = cfg.get("topology", "mesh")
protocol = cfg.get("protocol", "axi4")
routers = cfg["routers"]
dims = cfg.get("dimensions", {"x": 1, "y": 1})

print(f"[INFO] Generating {topology.upper()} topology for {name}")

# =====================================================
# 3. Build Router Mesh with Correct Connections
# =====================================================
mesh = {(r["coords"][0], r["coords"][1]): r for r in routers}
connections = []

if topology == "mesh":
    for (x, y), r in mesh.items():
        # East connections
        if (x + 1, y) in mesh:
            connections.append(((x, y), (x + 1, y), "east-west"))
        # South connections  
        if (x, y + 1) in mesh:
            connections.append(((x, y), (x, y + 1), "north-south"))
elif topology == "ring":
    coords = sorted(mesh.keys())
    for i in range(len(coords)):
        src = coords[i]
        dst = coords[(i + 1) % len(coords)]
        connections.append((src, dst, "ring"))
else:
    print(f"[WARN] Unsupported topology '{topology}', defaulting to mesh-like links")

print(f"[INFO] Generated {len(connections)} inter-router connections")

# =====================================================
# 4. Clean SystemVerilog Template (Fixed Formatting)
# =====================================================
noc_sv_template = """// ---------------------------------------------------
// FlooNoC auto-generated interconnect: {{ name }}
// Protocol: {{ protocol }}, Topology: {{ topology }}
// Dimensions: {{ dims.x }}x{{ dims.y }}
// ---------------------------------------------------
module {{ name }} (
  input  logic        clk_i,
  input  logic        rst_ni
{% for r in routers %}
{% for n in r.nodes %}
  , AXI_BUS.{% if n.type == 'master' %}Master{% else %}Slave{% endif %} {{ n.name }}
{% endfor %}
{% endfor %}
);

  // ------------------------------
  // Router Instances
  // ------------------------------
{% for r in routers %}
  floo_router #(
    .ID({{ r.id }}),
    .X({{ r.coords[0] }}),
    .Y({{ r.coords[1] }})
  ) router_{{ r.id }} (
    .clk_i(clk_i),
    .rst_ni(rst_ni)
{% for n in r.nodes %}
    {% if n.type == 'master' %}, .local_axi_master({{ n.name }})
    {% else %}, .local_axi_slave({{ n.name }}){% endif %}
{% endfor %}
    // Direction ports
    , .north_req_i(), .north_rsp_o()
    , .south_req_o(), .south_rsp_i()
    , .east_req_o(),  .east_rsp_i()
    , .west_req_i(),  .west_rsp_o()
  );
{% endfor %}

  // ------------------------------
  // Inter-Router Connections
  // ------------------------------
{% for conn in connections %}
{% set src_x, src_y = conn[0] %}
{% set dst_x, dst_y = conn[1] %}
{% set src_router = mesh[conn[0]] %}
{% set dst_router = mesh[conn[1]] %}
  // Connection: router_{{ src_router.id }} ({{ src_x }},{{ src_y }}) <-> router_{{ dst_router.id }} ({{ dst_x }},{{ dst_y }})
{% if src_x < dst_x %}
  assign router_{{ src_router.id }}.east_req_o = router_{{ dst_router.id }}.west_req_i;
  assign router_{{ src_router.id }}.east_rsp_i = router_{{ dst_router.id }}.west_rsp_o;
  assign router_{{ dst_router.id }}.west_req_o = router_{{ src_router.id }}.east_req_i;
  assign router_{{ dst_router.id }}.west_rsp_i = router_{{ src_router.id }}.east_rsp_o;
{% elif src_x > dst_x %}
  assign router_{{ src_router.id }}.west_req_o = router_{{ dst_router.id }}.east_req_i;
  assign router_{{ src_router.id }}.west_rsp_i = router_{{ dst_router.id }}.east_rsp_o;
  assign router_{{ dst_router.id }}.east_req_o = router_{{ src_router.id }}.west_req_i;
  assign router_{{ dst_router.id }}.east_rsp_i = router_{{ src_router.id }}.west_rsp_o;
{% elif src_y < dst_y %}
  assign router_{{ src_router.id }}.south_req_o = router_{{ dst_router.id }}.north_req_i;
  assign router_{{ src_router.id }}.south_rsp_i = router_{{ dst_router.id }}.north_rsp_o;
  assign router_{{ dst_router.id }}.north_req_o = router_{{ src_router.id }}.south_req_i;
  assign router_{{ dst_router.id }}.north_rsp_i = router_{{ src_router.id }}.south_rsp_o;
{% elif src_y > dst_y %}
  assign router_{{ src_router.id }}.north_req_o = router_{{ dst_router.id }}.south_req_i;
  assign router_{{ src_router.id }}.north_rsp_i = router_{{ dst_router.id }}.south_rsp_o;
  assign router_{{ dst_router.id }}.south_req_o = router_{{ src_router.id }}.north_req_i;
  assign router_{{ dst_router.id }}.south_rsp_i = router_{{ src_router.id }}.north_rsp_o;
{% endif %}
{% endfor %}

endmodule
"""

# =====================================================
# 5. Generate SystemVerilog (with clean output)
# =====================================================
tmpl = Template(noc_sv_template)
rendered_sv = tmpl.render(
    name=name,
    topology=topology,
    protocol=protocol,
    routers=routers,
    connections=connections,
    mesh=mesh,
    dims=dims
)

# Clean any escape characters and write file
cleaned_sv = re.sub(r'\x1b\[[0-9;]*[a-zA-Z]', '', rendered_sv)

sv_out = os.path.join(args.output, f"{name}.sv")
with open(sv_out, "w", encoding='utf-8') as f:
    f.write(cleaned_sv)
print(f"[OK] Generated {sv_out}")

# =====================================================
# 6. Optional FuseSoC Core File
# =====================================================
if args.fusesoc:
    core_content = f"""CAPI=2:

name: pulp-platform:{name}:0.1.0
description: Auto-generated NoC for FlooNoC
filesets:
  rtl:
    files:
      - {name}.sv
    file_type: systemVerilogSource
targets:
  default:
    filesets: [rtl]
"""
    core_out = os.path.join(args.output, f"{name}.core")
    with open(core_out, "w", encoding='utf-8') as f:
        f.write(core_content)
    print(f"[OK] Generated {core_out}")

print("[INFO] NoC generation complete ✅")
