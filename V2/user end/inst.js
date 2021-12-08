var con = new WebSocket("ws://80.5.202.49:4040");

con.onopen = function() {
	con.send("LIST"); //on boot request list
	window.scrollTo(0, document.body.scrollHeight);
};
con.onerror = function(error) {
	console.log("error" + error)
};
list=[];
con.onmessage = function(e) {
	console.log("message:" + e.data);
	var vals = e.data.split(">>>");
  if(vals.length>1)//if list sent
  {
    list=vals.split(":::"); //split down items
    populate(list); //populate screen
  }else{
    console.log(e.data); //output success function
  }
};


function populate(Array) //popluate the screen with the html format
{
	var a = "<option value='";
  var b = "'>";
	var c = "</option>";
	var string="";
	for (var i=0;i<Array.length;i++)
	{
		string+=a+Array[i]+b+Array[i]+c; //show in correct format
	}
	document.getElementById("mySelect").innerHTML=string;

}
function toPython(usrdata) {
	console.log("uploading" + usrdata);
	$.ajax({
		url: "http://80.5.202.205:4040",
		type: "POST",
		data: {
			information: "From SHEP client",
			userdata: usrdata
		},
		dataType: "json",
		success: function(data) {
			console.log("connected");
			console.log(data);
		}
	})
}
