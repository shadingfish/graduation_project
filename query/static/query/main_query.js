
let BASE_URL = "http://localhost:8000/"

document.getElementById('query-button').addEventListener('click', function() {
        document.querySelector('form').submit(); // 触发表单提交
    });
document.addEventListener('DOMContentLoaded', function() {
    document.getElementById('query-button').addEventListener('click', function() {
        let queryInput = document.getElementById('query-input').value;  // 获取查询语句
        // 构建请求 URL
        let url = document.getElementById('graph-url').getAttribute('data-url');
        // 发送带有查询语句的请求
        fetch(url, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCSRFToken()  // 从 cookie 中获取 CSRF 令牌
            },
            body: JSON.stringify({ 'search_query': queryInput })  // 发送查询语句
        })
        .then(response => response.json())
        .then(data => {
            console.log("Received data.");
            renderGraph(data.nodes, data.edges);
            console.log("Finished drawing.");
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

    // 转换边的数据结构
    const transformedEdges = edges.map(edge => ({
        source: edge.from,
        target: edge.to,
        label: edge.label // 确保边对象有一个 'label' 属性
    }));

    // 提取节点的 ChineseName 作为标注
    const getChineseName = title => {
        const match = title.match(/ChineseName: ([^,]+)(,|$)/);
        return match ? match[1].trim() : ''; // 使用 trim() 来去除可能的前后空白字符
    };
    
    // 设置 SVG 画布大小以适应 div
    const graphOutput = document.getElementById("graph-output");
    const width = graphOutput.clientWidth, height = graphOutput.clientHeight;
    const svg = d3.select("#graph-output").append("svg")
        .attr("width", width)
        .attr("height", height);

    // 颜色映射函数
    const color = d3.scaleOrdinal(d3.schemeCategory10);

    // 创建力布局
    const simulation = d3.forceSimulation(nodes)
        .force("link", d3.forceLink(transformedEdges).id(d => d.id).distance(200)) // 增加边的默认长度
        .force("charge", d3.forceManyBody().strength(-50)) // 调整排斥力，让节点稍微分散一些
        .force("center", d3.forceCenter(width / 2, height / 2));

    // 绘制边
    const link = svg.append("g")
        .attr("class", "links")
        .selectAll("line")
        .data(transformedEdges)
        .enter().append("line")
        .attr("stroke-width", 2)
        .attr("stroke", "black");

    // 绘制边的标注
    const edgeLabels = svg.append("g")
        .attr("class", "edge-labels")
        .selectAll("text")
        .data(transformedEdges)
        .enter().append("text")
        .style("font-size", "10px") // 在这里设置标注的字体大小为 10px
        .text(d => d.label); // 使用边的 'label'

    // 绘制节点
    const node = svg.append("g")
        .attr("class", "nodes")
        .selectAll("circle")
        .data(nodes)
        .enter().append("circle")
        .attr("r", 10) // 增加节点的大小
        .attr("fill", d => color(d.label));

    // 添加节点的标注
    const labels = svg.append("g")
        .attr("class", "node-labels")
        .selectAll("text")
        .data(nodes)
        .enter().append("text")
        .text(d => getChineseName(d.title)); // 使用 ChineseName

    // 更新节点、边及其标注的位置
    simulation.on("tick", () => {
        link.attr("x1", d => d.source ? d.source.x : 0)
            .attr("y1", d => d.source ? d.source.y : 0)
            .attr("x2", d => d.target ? d.target.x : 0)
            .attr("y2", d => d.target ? d.target.y : 0);
        
        node.attr("cx", d => d.x ? d.x : 0)
            .attr("cy", d => d.y ? d.y : 0);
        
        labels.attr("x", d => d.x ? d.x : 0)
              .attr("y", d => d.y ? d.y - 15 : 0); // 调整标注位置，避免与节点重叠
        
        edgeLabels.each(function(d) {
            if (d.source && d.target) { // 确保 source 和 target 都存在
                const x = (d.source.x + d.target.x) / 2;
                const y = (d.source.y + d.target.y) / 2;
                const angle = Math.atan2(d.target.y - d.source.y, d.target.x - d.source.x) * 180 / Math.PI;
                d3.select(this)
                    .attr("x", x)
                    .attr("y", y)
                    .attr("transform", `rotate(${angle},${x},${y})`);
            }
        });
    });
    
        // 等待模拟稳定后打印 SVG 内容
    setTimeout(() => {
        console.log("SVG Content after simulation:", d3.select("#graph-output").html());
        console.log("Finished drawing.");
    }, 3000); // 可以根据需要调整时间
}