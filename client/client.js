ajax_call = function(method, path, func, data) {
    url = 'http://127.0.0.1:5000';

    var xhttp = new XMLHttpRequest();

    xhttp.onreadystatechange = function() {
        if (xhttp.readyState == 4 && xhttp.status == 200) {

            var resp = JSON.parse(xhttp.responseText);

            func(resp);

            console.log(JSON.parse(xhttp.responseText));
        }
    };

    xhttp.open(method, url + path, true);

    if (method != "GET") {
        xhttp.setRequestHeader("Content-Type", "application/json");
        xhttp.send(JSON.stringify(data));
    }
    else
        xhttp.send();
}


window.onload = function(){
    if (localStorage.getItem('token'))
        display_view('profileview');
    else 
        display_view('welcomeview');
}

define_onclick_functions = function() {
    var account_tab = document.getElementById("account-tab");
    account_tab.onclick = function() {
        activate_account();
    }

    var home_tab = document.getElementById("home-tab");
    home_tab.onclick = function() {
        activate_home();
    }

    var browse_tab = document.getElementById("browse-tab");
    browse_tab.onclick = function() {
        activate_browse();
    }

    var send_button_home = document.getElementById("status-send-home");
    send_button_home.onclick = function() {
        send_button('home');
    }

    var send_button_browse = document.getElementById("status-send-browse");
    send_button_browse.onclick = function() {
        send_button('browse');
    }


    var refresh_button_home = document.getElementById("wall-refresh-home");
    refresh_button_home.onclick = function() {
        refresh_wall('home');
    }

    var refresh_button_browse = document.getElementById("wall-refresh-browse");
    refresh_button_home.onclick = function() {
        refresh_wall('browse', get_user_info().email);
    }


    var signout_button = document.getElementById("sign-out");
    signout_button.onclick = function() {
        serverstub.signOut(get_token());
        localStorage.removeItem('token');
        display_view('welcomeview');
    }

    var search_button = document.getElementById("search-send");
    search_button.onclick = function() {
        var email = document.getElementById("search-field").value;
        var resp = serverstub.getUserDataByEmail(get_token(), email);
        if (!resp.success) 
            display_error_search(resp.message)
        else 
            show_profile(resp.data);
    }
}

display_view = function(view) {
    document.getElementById('view').innerHTML = document.getElementById(view).innerHTML;

    if (view == 'welcomeview')
        document.getElementsByTagName("body")[0].style.background = "#6699ff";
    if (view == 'profileview') {
        define_onclick_functions();
        document.getElementsByTagName("body")[0].style.background = "#FFF";
        activate_account();
    }
}

check_reg_correctness = function() {
	var pass1 = document.getElementById("regpass1").value;
    var pass2 = document.getElementById("regpass2").value;
    var status = true;
    var msg = '';

    if (pass1 != pass2) {
    	msg = "Your passwords don't match. Check again";
    	status = false;
    }

    if (pass1.length < 8) {
    	msg = "Make sure password has length at least 8";
    	status = false;
    }

    display_error_msg_reg(msg);

    return status;
}

display_error_msg_reg = function(msg) {
	document.getElementById("error-reg").innerHTML = msg;
}

display_error_msg_log = function(msg) {
	document.getElementById("error-log").innerHTML = msg;
}

login = function(email, password) {
    var data = {'email': email, 'password': password};

    func = function(resp) {
        if (!resp.success) 
            display_error_msg_log(resp.message);
        else {
            localStorage.setItem('token', resp.data);

            display_view('profileview');
            activate_account();
        }
    }

    ajax_call("POST", "/sign_in", func, data);
}

login_form = function() {
    var form = document.forms['login-form'];
    var email = form['email'].value;
    var password = form['pass'].value;

    login(email, password); 
}

signup = function() {
	var form = document.forms['signup-form'];
    var data = {
        firstname: form['firstName'].value,
        familyname: form['familyName'].value,
        gender: form['gender'].value,
        city: form['city'].value,
        country: form['country'].value,
        email: form['email'].value,
        password: form['pass'].value
    };


    if (check_reg_correctness()) {
        func = function(resp) {
        	if (!resp.success) 
        		display_error_msg_reg(resp.message);
        	else
        		login(data.email, data.password);
        }

        ajax_call("POST", "/sign_up", func, data);
    }
}


send_button = function(where) {
        var msg = document.getElementById("status-field-" + where).value;
        var token = get_token();

        if (where == 'home')
            var email = get_user_info().email;
        else if (where == 'browse')
            var email = document.getElementById("search-field").value;

        var resp = serverstub.postMessage(token, msg, email);
        if (resp.success) {
            document.getElementById("status-field-" + where).value = '';
            refresh_wall(where, email);
        }
    }


refresh_wall = function(which, email) {
    if (which == 'home')
        var resp = serverstub.getUserMessagesByToken(get_token());
    else if (which == 'browse')
        var resp = serverstub.getUserMessagesByEmail(get_token(), email);

    document.getElementById("wall-list" + '-' + which).innerHTML = ''

    if (resp.success) {
        var data = resp.data;

        for (var msg of data)
            append_message_li(which, msg);
    }
    
    if (data.length > 8)
        prolonging_content(which);
}

append_message_li = function(which_wall, msg) {
    var newLi = document.createElement("li");
    var text = document.createTextNode('"' + msg.content + '" from ' + msg.writer);

    newLi.appendChild(text);
    var ulnew = document.getElementById("wall-list-" + which_wall);
    ulnew.appendChild(newLi); 
}
prolonging_content = function(where) {
    var att = document.createAttribute("style");
    att.value = "height: " + (300 + parseInt(window.getComputedStyle(document.getElementById("wall-" + where)).height)).toString() + "px;";
    document.getElementById("content").setAttributeNode(att);
}
reset_content_height = function() {
    var att = document.createAttribute("style");
    att.value = "height: 550px";
    document.getElementById("content").setAttributeNode(att);
}

get_token = function() {
    return localStorage.getItem('token');
}

get_user_info = function() {
    token = get_token();
    return serverstub.getUserDataByToken(token).data;
}

highlight_label = function(label) {
    document.getElementById('account-label').style.fontSize = "100%";
    document.getElementById('home-label').style.fontSize = "100%";
    document.getElementById('browse-label').style.fontSize = "100%";

    document.getElementById(label + '-label').style.fontSize = "120%";

    document.getElementById('account-label').style.fontWeight = "normal";
    document.getElementById('home-label').style.fontWeight = "normal";
    document.getElementById('browse-label').style.fontWeight = "normal";

    document.getElementById(label + '-label').style.fontWeight = "bold";

}

activate_account = function() {
    document.getElementById('account-view').style = "display: block;";
    document.getElementById('home-view').style = "display: none;";
    document.getElementById('browse-view').style = "display: none;";
    highlight_label('account');
    reset_content_height();
}


activate_home = function() {
    document.getElementById('account-view').style = "display: none;";
    document.getElementById('home-view').style = "display: block;";
    document.getElementById('browse-view').style = "display: none;";
    highlight_label('home');

    reset_content_height();
    fill_user_info_fields('home', get_user_info());
    refresh_wall('home');
}
fill_user_info_fields = function(tab, info) {

    document.getElementById(tab + '-email').innerHTML = info.email;
    document.getElementById(tab + '-firstname').innerHTML = info.firstname;
    document.getElementById(tab + '-familyname').innerHTML = info.familyname;
    document.getElementById(tab + '-gender').innerHTML = info.gender;
    document.getElementById(tab + '-city').innerHTML = info.city;
    document.getElementById(tab + '-country').innerHTML = info.country;
}

activate_browse = function() {
    document.getElementById('account-view').style = "display: none;";
    document.getElementById('home-view').style = "display: none;";
    document.getElementById('browse-view').style = "display: block;";
    highlight_label('browse');

    document.getElementById('profile-unfam').style = "display: none;";
    document.getElementById('search-content').style = "display: block;";

    document.getElementById('search-error').innerHTML = '';
    document.getElementById('search-field').value = '';

    reset_content_height();
}


change_password = function() {
    var form = document.forms['pass-change-form'];
    var current = form['current'].value,
        pass1 = form['pass1'].value,
        pass2 = form['pass2'].value

    var error_msg = '';

    if (pass1 != pass2)
        error_msg = "Passwords don't match";

    if (pass1.length < 8)
        error_msg = "Password has to be longer than 8 symbols";

    if (error_msg != '') {
        display_error_msg_change(error_msg);
        return false;
    }

    var resp = serverstub.changePassword(get_token(), current, pass1);
    if (!resp.success) {
        document.getElementById('change-error').style.color = "FF0000";
        display_error_msg_change(resp.message);
    }
    else {
        document.getElementById('change-error').style.color = "00FF00";
        display_error_msg_change(resp.message);
        document.getElementById("pass-change-form").reset();
    }

}

display_error_msg_change = function(msg) {
    document.getElementById("change-error").innerHTML = msg;
}

display_error_search = function(msg) {
    document.getElementById("search-error").innerHTML = msg;
}

show_profile = function(data) {
    document.getElementById('search-content').style = "display: none;";
    document.getElementById('profile-unfam').style = "display: block;";
    fill_user_info_fields('browse', data);
    refresh_wall('browse', data.email);
}
