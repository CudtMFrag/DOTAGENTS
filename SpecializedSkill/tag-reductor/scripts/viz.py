"""
Generate D3.js word cloud + force-directed co-occurrence graph from tag mapping JSON.

Usage:
  uv run python viz.py <tag_mapping.json> <output.html>

Input should use {"tags": ["multi word", "tag"]}. Legacy space-delimited tag
strings are accepted for compatibility, but cannot preserve multi-word tags.
"""
import json
import sys
from collections import defaultdict


def normalize_tags(value):
    if value is None:
        return []
    if isinstance(value, list):
        return [str(tag).strip() for tag in value if str(tag).strip()]
    if isinstance(value, str):
        return [tag.strip() for tag in value.split() if tag.strip()]
    raise TypeError(f"Unsupported tags value: {value!r}")


def generate(input_path, output_path):
    with open(input_path, encoding="utf-8") as f:
        data = json.load(f)

    tag_counts = defaultdict(int)
    cooccur = defaultdict(lambda: defaultdict(int))
    normalized_items = []

    for item in data:
        tags = normalize_tags(item.get("tags"))
        normalized_items.append(tags)
        for tag in tags:
            tag_counts[tag] += 1
        for i in range(len(tags)):
            for j in range(i + 1, len(tags)):
                a, b = sorted([tags[i], tags[j]])
                cooccur[a][b] += 1

    edges = []
    for a in cooccur:
        for b in cooccur[a]:
            weight = cooccur[a][b]
            if weight >= 2:
                edges.append({"source": a, "target": b, "weight": weight})

    nodes = [{"id": tag, "count": count} for tag, count in tag_counts.items()]
    n_items = len(data)
    n_tags = len(tag_counts)
    avg_tags = round(sum(len(tags) for tags in normalized_items) / n_items, 1) if n_items else 0

    graph_json = json.dumps(
        {"nodes": nodes, "edges": edges, "tag_counts": dict(tag_counts)},
        ensure_ascii=False,
    )

    html = f'''<!DOCTYPE html>
<html lang="zh">
<head>
<meta charset="UTF-8">
<title>Tag Viz - {n_tags} tags</title>
<script src="https://d3js.org/d3.v7.min.js"></script>
<style>
*{{margin:0;padding:0;box-sizing:border-box}}
body{{font-family:-apple-system,"Microsoft YaHei",sans-serif;background:#0d1117;color:#c9d1d9}}
.tabs{{display:flex;border-bottom:1px solid #30363d;padding:0 20px;background:#161b22}}
.tab{{padding:12px 24px;cursor:pointer;border:none;background:none;color:#8b949e;font-size:15px;border-bottom:2px solid transparent;transition:all .2s}}
.tab:hover{{color:#e6edf3}}
.tab.active{{color:#58a6ff;border-bottom-color:#58a6ff}}
.panel{{display:none}}
.panel.active{{display:block}}
#wc{{padding:40px 20px;text-align:center;min-height:600px;display:flex;flex-wrap:wrap;align-items:center;justify-content:center;align-content:center;gap:6px 14px}}
#wc span{{display:inline-block;cursor:pointer;transition:transform .2s,color .2s;font-weight:500}}
#wc span:hover{{transform:scale(1.2)}}
#graph{{width:100%;height:900px}}
.tip{{position:fixed;background:#21262d;color:#e6edf3;padding:8px 14px;border-radius:6px;font-size:13px;pointer-events:none;opacity:0;transition:opacity .15s;border:1px solid #30363d;z-index:100}}
.info{{text-align:center;padding:8px;color:#8b949e;font-size:12px}}
</style>
</head>
<body>
<div class="tabs">
<button class="tab active" data-panel="wc">Word Cloud</button>
<button class="tab" data-panel="graph">Co-occurrence Graph</button>
</div>
<div class="info">{n_items} items | {n_tags} tags | avg {avg_tags} tags/item</div>
<div id="wc" class="panel active"></div>
<div id="graph" class="panel"></div>
<div class="tip" id="tip"></div>
<script>
const D = {graph_json};

document.querySelector(".tabs").addEventListener("click",function(e){{
  if(!e.target.classList.contains("tab"))return;
  var p=e.target.getAttribute("data-panel");
  document.querySelectorAll(".tab").forEach(function(t){{t.classList.remove("active")}});
  document.querySelectorAll(".panel").forEach(function(p){{p.classList.remove("active")}});
  e.target.classList.add("active");
  document.getElementById(p).classList.add("active");
  if(p==="graph")initGraph();
}});

(function(){{
  var c=document.getElementById("wc");
  var entries=Object.entries(D.tag_counts).sort(function(a,b){{return b[1]-a[1]}});
  if(!entries.length){{
    c.textContent="No tags to visualize";
    return;
  }}
  var mx=entries[0][1],mn=entries[entries.length-1][1];
  var span=Math.max(1,mx-mn);
  var cl=["#58a6ff","#3fb950","#d2a8ff","#f0883e","#f85149","#a5d6ff","#ff7b72","#79c0ff","#56d364","#db6d28"];
  entries.forEach(function(e){{
    var t=e[0],n=e[1],s=document.createElement("span");
    s.textContent=t;
    var r=(n-mn)/span;
    s.style.fontSize=(18+r*44)+"px";
    s.style.color=cl[Math.min(Math.floor(r*cl.length),cl.length-1)];
    s.style.opacity=0.45+r*0.55;
    s.title=t+": "+n;
    c.appendChild(s);
  }});
}})();

var gi=false;
function initGraph(){{
  if(gi)return;gi=true;
  var el=document.getElementById("graph"),W=el.clientWidth,H=900;
  var svg=d3.select("#graph").append("svg").attr("viewBox",[0,0,W,H]);
  var g=svg.append("g");
  svg.call(d3.zoom().scaleExtent([0.1,4]).on("zoom",function(e){{g.attr("transform",e.transform)}}));
  var tip=d3.select("#tip"),color=d3.scaleOrdinal(d3.schemeTableau10);
  var links=D.edges.map(function(d){{return Object.assign({{}},d)}});
  var nodes=D.nodes.map(function(d){{return Object.assign({{}},d)}});
  var sim=d3.forceSimulation(nodes)
    .force("link",d3.forceLink(links).id(function(d){{return d.id}}).distance(function(d){{return 200/Math.sqrt(d.weight)}}))
    .force("charge",d3.forceManyBody().strength(-800))
    .force("center",d3.forceCenter(W/2,H/2))
    .force("collision",d3.forceCollide().radius(function(d){{return Math.sqrt(d.count)*7+16}}));
  var link=g.append("g").selectAll("line").data(links).join("line")
    .attr("stroke","#30363d").attr("stroke-width",function(d){{return Math.sqrt(d.weight)*0.7}})
    .attr("stroke-opacity",function(d){{return 0.15+d.weight*0.04}});
  var node=g.append("g").selectAll("g").data(nodes).join("g")
    .call(d3.drag()
      .on("start",function(e,d){{if(!e.active)sim.alphaTarget(0.3).restart();d.fx=d.x;d.fy=d.y;}})
      .on("drag",function(e,d){{d.fx=e.x;d.fy=e.y;}})
      .on("end",function(e,d){{if(!e.active)sim.alphaTarget(0);d.fx=null;d.fy=null;}}));
  node.append("circle").attr("r",function(d){{return Math.sqrt(d.count)*3+5}})
    .attr("fill",function(d){{return color(d.id)}}).attr("fill-opacity",0.85)
    .attr("stroke","#30363d").attr("stroke-width",1);
  node.append("text").text(function(d){{return d.id}})
    .attr("font-size",function(d){{return Math.min(14,8+d.count*0.15)}})
    .attr("dx",function(d){{return Math.sqrt(d.count)*3+8}}).attr("dy",".35em")
    .attr("fill","#c9d1d9");
  node.on("mouseenter",function(e,d){{tip.style("opacity",1).html("<b>"+d.id+"</b><br>"+d.count+" items")}})
    .on("mousemove",function(e){{tip.style("left",(e.pageX+12)+"px").style("top",(e.pageY-10)+"px")}})
    .on("mouseleave",function(){{tip.style("opacity",0)}});
  sim.on("tick",function(){{
    link.attr("x1",function(d){{return d.source.x}}).attr("y1",function(d){{return d.source.y}})
        .attr("x2",function(d){{return d.target.x}}).attr("y2",function(d){{return d.target.y}});
    node.attr("transform",function(d){{return"translate("+d.x+","+d.y+")"}});
  }});
}}
</script>
</body>
</html>'''

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(html)
    print(f"Generated: {output_path}")


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print(__doc__.strip())
        sys.exit(1)
    generate(sys.argv[1], sys.argv[2])
