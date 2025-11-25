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
# 3. Build Router Mesh
# =====================================================
mesh = {(r["coords"][0], r["coords"][1]): r for r in routers}
connections = []

if topology == "mesh":
    for (x, y), r in mesh.items():
        if (x + 1, y) in mesh:
            connections.append(((x, y), (x + 1, y), "east-west"))
        if (x, y + 1) in mesh:
            connections.append(((x, y), (x, y + 1), "south-north"))
elif topology == "ring":
    # Simple 1D ring connection
    coords = sorted(mesh.keys())
    for i in range(len(coords)):
        src = coords[i]
        dst = coords[(i + 1) % len(coords)]
        connections.append((src, dst, "ring"))
else:
    print(f"[WARN] Unsupported topology '{topology}', defaulting to mesh-like links")

# =====================================================
# 4. SystemVerilog Template (Inline)
# =====================================================
noc_sv_template = """\
// ---------------------------------------------------
// FlooNoC auto-generated interconnect: {{ name }}
// Protocol: {{ protocol }}, Topology: {{ topology }}
// ---------------------------------------------------
module {{ name }} (
  input  logic clk_i,
  input  logic rst_ni
  {%- for r in routers %}
  {%- set is_master = false %}
  {%- for n in r['nodes'] %}
    {%- if n['type'] == 'master' %}
      {%- set is_master = true %}
    {%- endif %}
  {%- endfor %}
  , {{ 'AXI_BUS.Master' if is_master else 'AXI_BUS.Slave' }} {{ r['nodes'][0]['name'] }}
  {%- endfor %}
);

  // ------------------------------
  // Router Instances
  // ------------------------------
  {%- for r in routers %}
  floo_router #(
    .ID({{ r['id'] }}),
    .X({{ r['coords'][0] }}),
    .Y({{ r['coords'][1] }})
  ) router_{{ r['id'] }} (
    .clk_i(clk_i),
    .rst_ni(rst_ni)
    // TODO: add link connections and local port binding
  );
  {%- endfor %}

  // ------------------------------
  // Inter-Router Connections
  // ------------------------------
  {%- for c in connections %}
  // Link between router_{{ mesh[c[0]]['id'] }} and router_{{ mesh[c[1]]['id'] }} ({{ c[2] }})
  assign router_{{ mesh[c[0]]['id'] }}.east = router_{{ mesh[c[1]]['id'] }}.west;
  assign router_{{ mesh[c[1]]['id'] }}.west = router_{{ mesh[c[0]]['id'] }}.east;
  {%- endfor %}

endmodule
"""

tmpl = Template(noc_sv_template)
rendered_sv = tmpl.render(
    name=name,
    topology=topology,
    protocol=protocol,
    routers=routers,
    connections=connections,
    mesh=mesh,
)

# =====================================================
# 5. Write SystemVerilog File
# =====================================================
sv_out = os.path.join(args.output, f"{name}.sv")
with open(sv_out, "w") as f:
    f.write(rendered_sv)
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
    with open(core_out, "w") as f:
        f.write(core_content)
    print(f"[OK] Generated {core_out}")

print("[INFO] NoC generation complete ✅")

