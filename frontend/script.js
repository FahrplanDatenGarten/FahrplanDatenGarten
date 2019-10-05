$(document).ready(function(){
    var url = "https://gist.githubusercontent.com/planetoftheweb/4069235/raw/0ca9457d10f9ff0be578a699954910d7d6626726/sampledata.json";
    $.ajax({
        url: url,
        dataType: 'json'
    })
    .done(function(data){
        console.log(data);
        var bio = data.speakers[0].bio;
        console.log(bio);
        
    });
});
