"use strict";
const POSITIONS = ["QB", "RB", "WR", "TE", "DST", "K"];
const ANALYSTS = ["BERRY", "KARABELL", "YATES", "COCKROFT", "CLAY", "BELL"];
const PALETTE = ["#F8E9A1","#F76C6C", "#EEE5DE", "#A8D0E6","#374785","#24305E"];
const margin = {top: 20, right: 40, bottom: 50, left: 55};
const width = 1000 - margin.left - margin.right;
const height = 500 - margin.top - margin.bottom;
const colors = d3.scaleOrdinal().range(PALETTE);

var svg = d3.select("div.chart").append("svg")
    .attr("width", width + margin.left + margin.right)
    .attr("height", height + margin.top + margin.bottom)
    .append("g")
    .attr("transform", "translate(" + margin.left + "," + margin.top + ")");

/*
Formats data to be an array of objects containing a key for
the position and an object containing the errors from each analyst.
*/
function formatData(data) {
    var formattedData = [];
    POSITIONS.map(function (pos) {
        var newEntry = {};
        newEntry.position = pos;
        newEntry.analysts = [];
        ANALYSTS.map(function (analyst) {
            newEntry.analysts.push(
                {analyst: analyst, value: data[pos][analyst]}
            );
        });
        formattedData.push(newEntry);
    });
    return formattedData;
}

/*
Creates a grouped bar chart that displays the errors for each analyst
for each position in a given week. The lower the error, the better
and analyst did in predicting how well a player did.
*/
function loadPositionsChart(week) {
    // Remove existing data
    svg.selectAll("*").remove();

    // Create bar chart elements
    var x0 = d3.scaleBand().range([0, width]).paddingInner(0.1);
    var x1 = d3.scaleBand();
    var y = d3.scaleLinear().range([height, 0]);

    var url = "http://localhost:5000/stats/" + week + "/";
    d3.json(url).then(function(data) {
        data = formatData(data);
        var minVal = d3.min(data, function(pos) {
            return d3.min(pos.analysts, function(d) { return d.value; });
        });
        var maxVal = d3.max(data, function(pos) {
            return d3.max(pos.analysts, function(d) { return d.value; });
        });

        x0.domain(POSITIONS);
        x1.domain(ANALYSTS).range([15, x0.bandwidth()]);
        y.domain([minVal - 0.02, maxVal + 0.02]);

        var xAxis = d3.axisBottom().scale(x0).tickSize(0);
        var yAxis = d3.axisLeft().scale(y);

        svg.append("g")
            .attr("class", "x axis")
            .attr("transform", "translate(0," + height + ")")
            .style("font-size", "14px")
            .call(xAxis);

        svg.append("text")
            .attr("transform",
                  "translate(" + (width/2) + " ," + 
                                 (height + margin.top + 10) + ")")
            .style("text-anchor", "middle")
            .style("font-weight","bold")
            .text("Positions");

        svg.append("g")
            .attr("class", "y axis")
            .style("opacity","0")
            .style("font-size", "12px")
            .call(yAxis)
            .append("text")
            .attr("transform", "rotate(-90)")
            .attr("y", 6)
            .attr("dy", ".71em")
            .style("text-anchor", "end")
            .style("font-weight","bold")
            .text("Value");

        svg.append("text")
            .attr("transform", "rotate(-90)")
            .attr("y", 0 - margin.left - 5)
            .attr("x",0 - (height / 2))
            .attr("dy", "1em")
            .style("text-anchor", "middle")
            .style("font-weight","bold")
            .text("Weekly Errors");

        // Set y axis
        svg.select(".y").style("opacity","1");

        // Load data into bar chart
        var slice = svg.selectAll(".slice")
            .data(data)
            .enter().append("g")
            .attr("class", "g")
            .attr("transform",function(d) {
                return "translate(" + x0(d.position) + ",0)";
            });

        slice.selectAll("g")
            .data(function(d) { return d.analysts; })
            .enter().append("rect")
            .attr("width", x1.bandwidth())
            .attr("x", function(d) { return x1(d.analyst); })
            .style("fill", function(d) { return colors(d.analyst); });

        slice.selectAll("rect")
            .attr("y", function(d) { return y(d.value); })
            .attr("height", function(d) { return height - y(d.value); });

        // Legend
        var legend = svg.selectAll(".legend")
            .data(data[0].analysts.map(function(d) { return d.analyst; }))
            .enter().append("g")
            .attr("class", "legend")
            .attr("transform", function(d,i)
                { return "translate(0," + i * 20 + ")";
            })
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
}

/*
Creates a bar chart that displays the total error amassed over all
positions for the season for each analyst
*/
function loadSumsChart() {
    svg.selectAll("*").remove();
    var url = "http://localhost:5000/stats/sum/season/";
    d3.json(url).then(function(data) {
        var x1 = d3.scaleBand().range([15, width]).paddingInner(0.1);
        var y = d3.scaleLinear().range([height, 0]);

        var formattedData = []
        const minVal = d3.min(d3.values(data));
        const maxVal = d3.max(d3.values(data));
        ANALYSTS.map(function (analyst) {
            formattedData.push({analyst: analyst, value: data[analyst]});
        });

        x1.domain(ANALYSTS);
        y.domain([minVal - 0.1, maxVal + 0.1]);
        var xAxis = d3.axisBottom().scale(x1).tickSize(0);
        var yAxis = d3.axisLeft().scale(y);

        svg.append("g")
            .attr("class", "x axis")
            .attr("transform", "translate(0," + height + ")")
            .style("font-size", "14px")
            .call(xAxis);

        svg.append("text")
            .attr("transform",
                  "translate(" + (width/2) + " ," + 
                                 (height + margin.top + 10) + ")")
            .style("text-anchor", "middle")
            .style("font-weight","bold")
            .text("Analysts");

        svg.append("g")
            .attr("class", "y axis")
            .style("opacity","0")
            .style("font-size", "12px")
            .call(yAxis)
            .append("text")
            .attr("transform", "rotate(-90)")
            .attr("y", 6)
            .attr("dy", ".71em")
            .style("text-anchor", "end")
            .style("font-weight","bold")
            .style("font-size", "14px")
            .text("Value");

        svg.append("text")
            .attr("transform", "rotate(-90)")
            .attr("y", 0 - margin.left - 5)
            .attr("x",0 - (height / 2))
            .attr("dy", "1em")
            .style("text-anchor", "middle")
            .style("font-weight","bold")
            .text("Accumulated Errors");  

        svg.select(".y").style("opacity","1");

        // Load data into bar chart
        svg.selectAll("bar")
            .data(formattedData)
            .enter().append("rect")
            .style("fill", function(d) { return colors(d.analyst); })
            .attr("x", function(d) { return x1(d.analyst); })
            .attr("width", x1.bandwidth())
            .attr("y", function(d) { return y(d.value); })
            .attr("height", function(d) { return height - y(d.value); });

    });
}
