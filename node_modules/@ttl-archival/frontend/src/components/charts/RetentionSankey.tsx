import React, { useEffect, useRef } from 'react';
import * as d3 from 'd3';
import { 
  sankey as d3Sankey, 
  sankeyLinkHorizontal as d3SankeyLinkHorizontal,
  sankeyCenter as d3SankeyCenter
} from 'd3-sankey';

interface RetentionSankeyProps {
  data?: any;
}

const RetentionSankey: React.FC<RetentionSankeyProps> = ({ data }) => {
  const svgRef = useRef<SVGSVGElement>(null);

  useEffect(() => {
    if (!svgRef.current) return;

    const width = 800;
    const height = 400;

    const svg = d3.select(svgRef.current);
    svg.selectAll('*').remove();

    // Mock data if none provided
    const sankeyData = data || {
      nodes: [
        { name: "Active Data" },
        { name: "Archive (Tier 1)" },
        { name: "Archive (Tier 2)" },
        { name: "Expired (Awaiting Deletion)" },
        { name: "Cleaned Up" }
      ],
      links: [
        { source: 0, target: 1, value: 100 },
        { source: 0, target: 2, value: 50 },
        { source: 1, target: 3, value: 80 },
        { source: 2, target: 3, value: 40 },
        { source: 3, target: 4, value: 110 }
      ]
    };

    const sankey = (d3Sankey() as any)
      .nodeWidth(15)
      .nodePadding(10)
      .extent([[1, 1], [width - 1, height - 6]]);

    const { nodes, links } = sankey(sankeyData);

    const color = d3.scaleOrdinal(d3.schemeCategory10);

    // Links
    svg.append("g")
      .attr("fill", "none")
      .attr("stroke-opacity", 0.5)
      .selectAll("path")
      .data(links)
      .enter().append("path")
      .attr("d", d3SankeyLinkHorizontal())
      .attr("stroke", (d: any) => color(d.source.index))
      .attr("stroke-width", (d: any) => Math.max(1, d.width))
      .append("title")
      .text((d: any) => `${d.source.name} → ${d.target.name}\n${d.value} GB`);

    // Nodes
    const node = svg.append("g")
      .selectAll("g")
      .data(nodes)
      .enter().append("g");

    node.append("rect")
      .attr("x", (d: any) => d.x0)
      .attr("y", (d: any) => d.y0)
      .attr("height", (d: any) => d.y1 - d.y0)
      .attr("width", (d: any) => d.x1 - d.x0)
      .attr("fill", (d: any) => color(d.index))
      .attr("stroke", "#000");

    node.append("text")
      .attr("x", (d: any) => d.x0 - 6)
      .attr("y", (d: any) => (d.y1 + d.y0) / 2)
      .attr("dy", "0.35em")
      .attr("text-anchor", "end")
      .attr("fill", "currentColor")
      .attr("font-size", "12px")
      .attr("font-weight", "bold")
      .text((d: any) => d.name)
      .filter((d: any) => d.x0 < width / 2)
      .attr("x", (d: any) => d.x1 + 6)
      .attr("text-anchor", "start");

  }, [data]);

  return (
    <div className="w-full overflow-x-auto">
      <svg 
        ref={svgRef} 
        viewBox="0 0 800 400" 
        className="mx-auto text-card-foreground"
        style={{ minWidth: '600px' }}
      />
    </div>
  );
};

export default RetentionSankey;
