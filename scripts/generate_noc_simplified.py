#!/usr/bin/env python3
import os, yaml, argparse
from jinja2 import Template

# -----------------------------
# Argument parser
# -----------------------------
parser = argparse.ArgumentParser(description="FlooNoC RTL generator")
parser.add_argument("--config", required=True, help="YAML configuration file")
parser.add_argument("--output", required=True, help="Output directory")
parser.add_argument("--fusesoc", action="store_true", help="Generate FuseSoC .core file")
args = parser.parse_args()

os.makedirs(args.output, exist_ok=True)

# -----------------------------
# Load YAML config
# -----------------------------
with open(args.config, "r") as f:
    cfg = yaml.safe_load(f)["noc"]

name = cfg.get("name", "noc_generated")
routers = cfg["routers"]
dims = cfg.get("dimensions", {"x": 1, "y": 1})
protocol = cfg.get("protocol", "axi4")

# -----------------------------
# Build mesh topology
# -----------------------------
mesh = {(r["coords"][0], r["coords"][1]): r for r in routers}
connections = []

for (x, y), r in mesh.items():
    if (x+1, y) in mesh:
        connections.append(((x, y), (x+1, y)))
    if (x, y+1) in mesh:
        connections.append(((x, y), (x, y+1)))

# -----------------------------
# Jinja2 SystemVerilog template
# -----------------------------
template_sv = """
module {{ name }} (
  input  logic clk_i,
  input  logic rst_ni,
  {%- for r in routers %}
  {{ "AXI_BUS.Master" if "master" in [n.type for n in r.nodes] else "AXI_BUS.Slave" }}
  {{ r.nodes[0].name }},
  {%- endfor %}
);

  // Router instantiations
  {%- for r in routers %}
  floo_router #(.ID({{r.id}}), .X({{r.coords[0]}}), .Y({{r.coords[1]}})) router_{{r.id}} (
    .clk_i(clk_i), .rst_ni(rst_ni)
  );
  {%- endfor %}

  // Mesh links
  {%- for c in connections %}
  assign router_{{ mesh[c[0]].id }}.east = router_{{ mesh[c[1]].id }}.west;
  assign router_{{ mesh[c[1]].id }}.west = router_{{ mesh[c[0]].id }}.east;
  {%- endfor %}

endmodule
"""

tmpl = Template(template_sv)
rendered = tmpl.render(name=name, routers=routers, connections=connections, mesh=mesh)

# -----------------------------
# Write SystemVerilog output
# -----------------------------
sv_out = os.path.join(args.output, f"{name}.sv")
with open(sv_out, "w") as f:
    f.write(rendered)

print(f"[INFO] Generated {sv_out}")

# -----------------------------
# Optional FuseSoC core file
# -----------------------------
if args.fusesoc:
    core_out = os.path.join(args.output, f"{name}.core")
    with open(core_out, "w") as f:
        f.write(f"name: pulp-platform:{name}:0.1.0\nfilesets:\n  rtl:\n    files:\n      - {name}.sv\n")
    print(f"[INFO] Generated {core_out}")

