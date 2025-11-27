// ---------------------------------------------------
// FlooNoC auto-generated interconnect: axi_noc
// Protocol: axi4, Topology: mesh
// Dimensions: 2x3
// ---------------------------------------------------
module axi_noc (
  input  logic        clk_i,
  input  logic        rst_ni


  , AXI_BUS.Master CPU



  , AXI_BUS.Master GPU



  , AXI_BUS.Slave DDR4



  , AXI_BUS.Slave L3_CACHE



  , AXI_BUS.Slave PCIE



  , AXI_BUS.Slave NPU


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

    , .local_axi_master(CPU)
    

    // Direction ports
    , .north_req_i(), .north_rsp_o()
    , .south_req_o(), .south_rsp_i()
    , .east_req_o(),  .east_rsp_i()
    , .west_req_i(),  .west_rsp_o()
  );

  floo_router #(
    .ID(1),
    .X(1),
    .Y(0)
  ) router_1 (
    .clk_i(clk_i),
    .rst_ni(rst_ni)

    , .local_axi_master(GPU)
    

    // Direction ports
    , .north_req_i(), .north_rsp_o()
    , .south_req_o(), .south_rsp_i()
    , .east_req_o(),  .east_rsp_i()
    , .west_req_i(),  .west_rsp_o()
  );

  floo_router #(
    .ID(2),
    .X(0),
    .Y(1)
  ) router_2 (
    .clk_i(clk_i),
    .rst_ni(rst_ni)

    , .local_axi_slave(DDR4)

    // Direction ports
    , .north_req_i(), .north_rsp_o()
    , .south_req_o(), .south_rsp_i()
    , .east_req_o(),  .east_rsp_i()
    , .west_req_i(),  .west_rsp_o()
  );

  floo_router #(
    .ID(3),
    .X(1),
    .Y(1)
  ) router_3 (
    .clk_i(clk_i),
    .rst_ni(rst_ni)

    , .local_axi_slave(L3_CACHE)

    // Direction ports
    , .north_req_i(), .north_rsp_o()
    , .south_req_o(), .south_rsp_i()
    , .east_req_o(),  .east_rsp_i()
    , .west_req_i(),  .west_rsp_o()
  );

  floo_router #(
    .ID(4),
    .X(0),
    .Y(2)
  ) router_4 (
    .clk_i(clk_i),
    .rst_ni(rst_ni)

    , .local_axi_slave(PCIE)

    // Direction ports
    , .north_req_i(), .north_rsp_o()
    , .south_req_o(), .south_rsp_i()
    , .east_req_o(),  .east_rsp_i()
    , .west_req_i(),  .west_rsp_o()
  );

  floo_router #(
    .ID(5),
    .X(1),
    .Y(2)
  ) router_5 (
    .clk_i(clk_i),
    .rst_ni(rst_ni)

    , .local_axi_slave(NPU)

    // Direction ports
    , .north_req_i(), .north_rsp_o()
    , .south_req_o(), .south_rsp_i()
    , .east_req_o(),  .east_rsp_i()
    , .west_req_i(),  .west_rsp_o()
  );


  // ------------------------------
  // Inter-Router Connections
  // ------------------------------





  // Connection: router_0 (0,0) <-> router_1 (1,0)

  assign router_0.east_req_o = router_1.west_req_i;
  assign router_0.east_rsp_i = router_1.west_rsp_o;
  assign router_1.west_req_o = router_0.east_req_i;
  assign router_1.west_rsp_i = router_0.east_rsp_o;






  // Connection: router_0 (0,0) <-> router_2 (0,1)

  assign router_0.south_req_o = router_2.north_req_i;
  assign router_0.south_rsp_i = router_2.north_rsp_o;
  assign router_2.north_req_o = router_0.south_req_i;
  assign router_2.north_rsp_i = router_0.south_rsp_o;






  // Connection: router_1 (1,0) <-> router_3 (1,1)

  assign router_1.south_req_o = router_3.north_req_i;
  assign router_1.south_rsp_i = router_3.north_rsp_o;
  assign router_3.north_req_o = router_1.south_req_i;
  assign router_3.north_rsp_i = router_1.south_rsp_o;






  // Connection: router_2 (0,1) <-> router_3 (1,1)

  assign router_2.east_req_o = router_3.west_req_i;
  assign router_2.east_rsp_i = router_3.west_rsp_o;
  assign router_3.west_req_o = router_2.east_req_i;
  assign router_3.west_rsp_i = router_2.east_rsp_o;






  // Connection: router_2 (0,1) <-> router_4 (0,2)

  assign router_2.south_req_o = router_4.north_req_i;
  assign router_2.south_rsp_i = router_4.north_rsp_o;
  assign router_4.north_req_o = router_2.south_req_i;
  assign router_4.north_rsp_i = router_2.south_rsp_o;






  // Connection: router_3 (1,1) <-> router_5 (1,2)

  assign router_3.south_req_o = router_5.north_req_i;
  assign router_3.south_rsp_i = router_5.north_rsp_o;
  assign router_5.north_req_o = router_3.south_req_i;
  assign router_5.north_rsp_i = router_3.south_rsp_o;






  // Connection: router_4 (0,2) <-> router_5 (1,2)

  assign router_4.east_req_o = router_5.west_req_i;
  assign router_4.east_rsp_i = router_5.west_rsp_o;
  assign router_5.west_req_o = router_4.east_req_i;
  assign router_5.west_rsp_i = router_4.east_rsp_o;



endmodule
