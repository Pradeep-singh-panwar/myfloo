// ---------------------------------------------------
// FlooNoC auto-generated interconnect: my_soc_noc
// Protocol: axi4, Topology: mesh
// ---------------------------------------------------
module my_soc_noc (
  input  logic clk_i,
  input  logic rst_ni
  , AXI_BUS.Slave cpu0
  , AXI_BUS.Slave cpu1
  , AXI_BUS.Slave uart
  , AXI_BUS.Slave ddr
);

  // ------------------------------
  // Router Instances
  // ------------------------------
  floo_router #(
    .ID(0),
    .X(0),
    .Y(0)
  ) router_0 (
    .clk_i(clk_i),
    .rst_ni(rst_ni)
    // TODO: add link connections and local port binding
  );
  floo_router #(
    .ID(1),
    .X(1),
    .Y(0)
  ) router_1 (
    .clk_i(clk_i),
    .rst_ni(rst_ni)
    // TODO: add link connections and local port binding
  );
  floo_router #(
    .ID(2),
    .X(0),
    .Y(1)
  ) router_2 (
    .clk_i(clk_i),
    .rst_ni(rst_ni)
    // TODO: add link connections and local port binding
  );
  floo_router #(
    .ID(3),
    .X(1),
    .Y(1)
  ) router_3 (
    .clk_i(clk_i),
    .rst_ni(rst_ni)
    // TODO: add link connections and local port binding
  );

  // ------------------------------
  // Inter-Router Connections
  // ------------------------------
  // Link between router_0 and router_1 (east-west)
  assign router_0.east = router_1.west;
  assign router_1.west = router_0.east;
  // Link between router_0 and router_2 (south-north)
  assign router_0.east = router_2.west;
  assign router_2.west = router_0.east;
  // Link between router_1 and router_3 (south-north)
  assign router_1.east = router_3.west;
  assign router_3.west = router_1.east;
  // Link between router_2 and router_3 (east-west)
  assign router_2.east = router_3.west;
  assign router_3.west = router_2.east;

endmodule
