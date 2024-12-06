function doPushState(tab) {
    var state = {},
        title = "Page title",
        path  = "?" + tab;
    
    history.pushState(state, title, path);
};

function navbar(evt, name) {
	var i, x, tablinks;
 	x = document.getElementsByClassName("content");
 	for (i = 0; i < x.length; i++) {
 		x[i].style.display = "none";
 	}
 	tablinks = document.getElementsByClassName("tablink");
 	for (i = 0; i < x.length; i++) {
 		tablinks[i].className = tablinks[i].className.replace(" active", "");
 	}
	document.getElementById(name).style.display = "block";
	var navbardiv
	navbardiv = document.getElementById("TopNavbar");
	navbardiv.className = "topnav black"
	evt.currentTarget.className += " active";
	doPushState(name)
}

function toggleNavMenu() {
	var navbardiv
	navbardiv = document.getElementById("TopNavbar");

 	if (navbardiv.className === "topnav black"){
 		navbardiv.className += " responsive";
 	} else {
 		navbardiv.className = "topnav black";
 	}
}

$(document).ready(function() {
	var url = window.location.href;
	option = url.split('?')[1];
	if ( option == null ) {
		option = ""
	};
	var allowable = []
	x = document.getElementsByClassName("content");
 	for (i = 0; i < x.length; i++) {
 		x[i].style.display = "none";
 		allowable.push(x[i].id)
 	}
 	if ( !allowable.includes(option) ){
 		document.getElementById("announcements").style.display = "block";
 		document.getElementById("nav_announcements").className += " active";
 	} else {
 		document.getElementById(option).style.display = "block";
 		document.getElementById("nav_" + option).className += " active";
 	}
});

$(document).click(function(event) { 
	if(!$(event.target).closest('#TopNavbar').length) {
	    if( $('#TopNavbar').hasClass('responsive') ) {
	        $('#TopNavbar').removeClass('responsive');
	    }
	}        
});