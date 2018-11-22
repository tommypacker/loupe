var width = 500;
var height = 500;
var margin = {top: 20, right: 20, bottom: 30, left: 40},
    width = 960 - margin.left - margin.right,
    height = 500 - margin.top - margin.bottom;

var x = d3.scaleBand()
    .range([0, width])
    .padding(0.1);
var y = d3.scaleLinear()
    .range([height, 0]);

var svg = d3.select("body").append("svg")
    .attr("width", width + margin.left + margin.right)
    .attr("height", height + margin.top + margin.bottom)
  .append("g")
    .attr("transform", 
          "translate(" + margin.left + "," + margin.top + ")");

d3.json("http://localhost:5000/stats/1/")
    .then(function(data) {
        data = data.QB;
        var analysts = Object.keys(data);
        var stats = analysts.map(function ( key ) { return data[key]; });
        var maxVal = Math.max.apply(null, stats);

        x.domain(analysts);
        y.domain([0.9, maxVal]);

        newData = []
        analysts.map(function ( key ) { newData.push({analyst: key, value: data[key]}); });
        console.log(newData);

        svg.selectAll(".bar")
            .data(newData)
            .enter().append("rect")
            .attr("class", "bar")
            .attr("x", function(d) { return x(d.analyst); })
            .attr("width", x.bandwidth())
            .attr("y", function(d) { return y(d.value); })
            .attr("height", function(d) { return height - y(d.value); });

        // add the x Axis
        svg.append("g")
        .attr("transform", "translate(0," + height + ")")
        .call(d3.axisBottom(x));

        // add the y Axis
        svg.append("g")
        .call(d3.axisLeft(y));
    });