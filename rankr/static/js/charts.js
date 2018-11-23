const margin = {top: 20, right: 20, bottom: 30, left: 40},
    width = 960 - margin.left - margin.right,
    height = 500 - margin.top - margin.bottom;
var x0 = d3.scaleBand()
    .range([0, width])
    .paddingInner(0.2);
var x1 = d3.scaleBand();
var y = d3.scaleLinear()
    .range([height, 0]);
const colors = d3.scaleOrdinal()
    .range(["#ca0020","#f4a582","#d5d5d5","#92c5de","#0571b0", "#556B2F"]);

var svg = d3.select('body').append("svg")
    .attr("width", width + margin.left + margin.right)
    .attr("height", height + margin.top + margin.bottom)
    .append("g")
    .attr("transform", "translate(" + margin.left + "," + margin.top + ")");

d3.json("http://localhost:5000/stats/1/")
    .then(function(data) {
        var positions = Object.keys(data);
        var analysts = Object.keys(data.QB);
        data = formatData(data, positions, analysts);
        var maxVal = d3.max(formattedData, function(pos) { return d3.max(pos.analysts, function(d) { return d.value; }); });

        x0.domain(positions);
        x1.domain(analysts).range([0, x0.bandwidth()]);
        y.domain([0.9, maxVal + 0.02]);

        var xAxis = d3.axisBottom().scale(x0).tickSize(0);
        var yAxis = d3.axisLeft().scale(y);

        svg.append("g")
            .attr("class", "x axis")
            .attr("transform", "translate(0," + height + ")")
            .call(xAxis);

        svg.append("g")
            .attr("class", "y axis")
            .style('opacity','0')
            .call(yAxis)
        .append("text")
            .attr("transform", "rotate(-90)")
            .attr("y", 6)
            .attr("dy", ".71em")
            .style("text-anchor", "end")
            .style('font-weight','bold')
            .text("Value");

        svg.select('.y').style('opacity','1');

        var slice = svg.selectAll(".slice")
            .data(formattedData)
            .enter().append("g")
            .attr("class", "g")
            .attr("transform",function(d) { return "translate(" + x0(d.position) + ",0)"; });

        slice.selectAll("g")
            .data(function(d) { return d.analysts; })
        .enter().append("rect")
            .attr("width", x1.bandwidth())
            .attr("x", function(d) { return x1(d.analyst); })
            .style("fill", function(d) { return colors(d.analyst) })

        slice.selectAll("rect")
            .attr("y", function(d) { return y(d.value); })
            .attr("height", function(d) { return height - y(d.value); });

        //Legend
        var legend = svg.selectAll(".legend")
        .data(formattedData[0].analysts.map(function(d) { return d.analyst; }))
        .enter().append("g")
        .attr("class", "legend")
        .attr("transform", function(d,i) { return "translate(0," + i * 20 + ")"; })
        .style("opacity","0");

        legend.append("rect")
        .attr("x", width - 18)
        .attr("width", 18)
        .attr("height", 18)
        .style("fill", function(d) { return colors(d); });

        legend.append("text")
        .attr("x", width - 24)
        .attr("y", 9)
        .attr("dy", ".35em")
        .style("text-anchor", "end")
        .text(function(d) {return d; });

        legend.style("opacity","1");
    });

function formatData(data, positions, analysts) {
    formattedData = []
    positions.map(function (pos) {
        var newEntry = {};
        newEntry["position"] = pos;
        newEntry["analysts"] = [];
        analysts.map(function (analyst) {
            newEntry["analysts"].push({analyst: analyst, value: data[pos][analyst]});
        });
        formattedData.push(newEntry);
    });
    return formattedData;
}