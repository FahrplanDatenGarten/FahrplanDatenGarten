height = 800;
width = 700;

let svg1 = d3.select("#net")
    .append("svg")
    // Responsive SVG needs these 2 attributes and no width and height attr.
    .attr("preserveAspectRatio", "xMinYMin meet")
    .attr("viewBox", "0 0 " + width + " " + height)
    // Class to make it responsive.
    .classed("svg-content-responsive", true)

let projection = d3.geoMercator()
    .scale(3000)
    .center([10, 51])
    .translate([width / 2, height / 2]);

let path = d3.geoPath()
    .projection(projection);


let promises = [
    d3.json(d3_geojson_url),
    d3.json(d3_api_url)
];

Promise.all(promises).then(ready);

function ready(param) {

    svg1.append("g")
        .selectAll("path")
        .data(param[0]["features"])
        .enter()
        .append("path")
        .attr("d", d3.geoPath()
            .projection(projection))
        .attr("fill", "#9e9e9e");

    let lineGenerator = d3.line();
    let pathGroup = svg1.append("g");
    let myColor = d3.scaleSequential()
        .interpolator(d3.interpolateRdYlGn)
        .domain([130, 30]);
    let paths = pathGroup.selectAll("path")
        .data(param[1]['connections'])
        .enter()
        .append("path")
        .attr("d", function (d, i) {
            return lineGenerator(d.link.map(projection))
        })
        .attr("stroke", function (d) {
            return myColor(d.duration / this.getTotalLength())
        })
        .attr("stroke-width", 7)
        .attr("opacity", 1)
        .attr("display", "none");

    svg1.append("g")
        .selectAll("circle")
        .data(param[1]['stations'])
        .enter()
        .append("circle")
        .attr("r", 5)
        .attr("fill", "#EC0016")
        .attr("transform", function (d, i) {
            return "translate(" + projection(d.location) + ")"
        })
        .on("click", function draw_lines(d, i) {
            paths.filter(path_data => {
                return JSON.stringify(path_data.link[0]) === JSON.stringify(d.location);
            })
                .attr("display", "block");
            paths.filter(path_data => {
                return JSON.stringify(path_data.link[0]) !== JSON.stringify(d.location);
            })
                .attr("display", "none");
        })
        .on("mouseover", handleMouseOver)
        .on("mouseout", handleMouseOut);

    function handleMouseOver(d, i) { // Add interactivity
        // show station names
        svg1.append("text").text(d.name)
            .attr("transform", "translate(" + projection(d.location) + ")")
    }


    function handleMouseOut(d, i) {
        // removing station names
        svg1.selectAll("text").remove()
    }

}
