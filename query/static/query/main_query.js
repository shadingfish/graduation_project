
let BASE_URL = "http://localhost:8000/"
document.addEventListener('DOMContentLoaded', function() {
    document.getElementById('query-button').addEventListener('click', function() {
        console.log("Base url: " + BASE_URL)
        let url = BASE_URL + 'query/path-to-query-neo4j-view/'
        console.log("Using url: " + url)
        fetch(url)
        .then(response => response.json())
        .then(data => {
            console.log("Receive data.")
            // 使用 data['data'] 更新页面内容
            renderGraph(data.nodes, data.edges);
        })
        .catch(error => console.error('Error:', error));
    });

    document.getElementById('clear-button').addEventListener('click', function() {
        document.getElementById('answer-output').innerHTML = '';
        document.getElementById('graph-output').innerHTML = '';
    });

    document.getElementById('chatbot-button').addEventListener('click', function() {
        // 聊天界面的逻辑
    });
});

function renderGraph(nodes, edges) {
    console.log("Drawing graph.")
    // 首先清除现有的图形
    d3.select("#graph-output").selectAll("*").remove();

    // 设置 SVG 画布
    const width = 800, height = 600;
    const svg = d3.select("#graph-output").append("svg")
        .attr("width", width)
        .attr("height", height);

    // 创建一个模拟力布局
    const simulation = d3.forceSimulation(nodes)
        .force("link", d3.forceLink(edges).id(d => d.id))
        .force("charge", d3.forceManyBody())
        .force("center", d3.forceCenter(width / 2, height / 2));

    // 绘制边
    const link = svg.append("g")
        .attr("class", "links")
        .selectAll("line")
        .data(edges)
        .enter().append("line")
        .attr("stroke-width", 2);

    // 绘制节点
    const node = svg.append("g")
        .attr("class", "nodes")
        .selectAll("circle")
        .data(nodes)
        .enter().append("circle")
        .attr("r", 5)
        .attr("fill", "red");

    // 更新节点和边的位置
    simulation.on("tick", () => {
        link.attr("x1", d => d.source.x)
            .attr("y1", d => d.source.y)
            .attr("x2", d => d.target.x)
            .attr("y2", d => d.target.y);

        node.attr("cx", d => d.x)
            .attr("cy", d => d.y);
    });
    
    console.log("Finished drawing.")
}