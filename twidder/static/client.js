/* variables for Diffie-Hellman algorithm */
// generator
var g = 3;
// divider
var p = 17;

/* declaration of client-side routes and actions for them */
page('/', function() {
    if (get_token()) {
        page('/account');
        return;
    }
    window.history.pushState(window.history.state, 'Root');
    window.history.state = 'root';
});

page('/account', function() {
    if (!get_token()) {
        page('/');
        return;
    }

    display_view('profileview');
    document.getElementById('account-view').style = "display: block;";
    document.getElementById('home-view').style = "display: none;";
    document.getElementById('browse-view').style = "display: none;";
    document.getElementById('stats-view').style = "display: none;";

    highlight_label('account');
    reset_content_height();

    window.history.pushState(window.history.state, 'Account');
    window.history.state = 'account';
});

page('/home', function() {
    if (!get_token()) {
        page('/');
        return;
    }

    display_view('profileview');
    document.getElementById('account-view').style = "display: none;";
    document.getElementById('home-view').style = "display: block;";
    document.getElementById('browse-view').style = "display: none;";
    document.getElementById('stats-view').style = "display: none;";

    highlight_label('home');

    reset_content_height();
    fill_user_info_fields('home', get_user_info());
    refresh_wall('home');

    drag_and_drop();

    window.history.pushState(window.history.state, 'Home');
    window.history.state = 'home';
});

page('/browse', function() {
    if (!get_token()) {
        page('/');
        return;
    }

    display_view('profileview');
    document.getElementById('account-view').style = "display: none;";
    document.getElementById('home-view').style = "display: none;";
    document.getElementById('browse-view').style = "display: block;";
    document.getElementById('stats-view').style = "display: none;";
    highlight_label('browse');

    document.getElementById('profile-unfam').style = "display: none;";
    document.getElementById('search-content').style = "display: block;";

    document.getElementById('search-error').innerHTML = '';
    document.getElementById('search-field').value = '';

    reset_content_height();

    window.history.pushState(window.history.state, 'Browse');
    window.history.state = 'browse';
});

var stats_socket;
page('/stats', function() {
    if (!get_token()) {
        page('/');
        return;
    }

    display_view('profileview');
    document.getElementById('account-view').style = "display: none;";
    document.getElementById('home-view').style = "display: none;";
    document.getElementById('browse-view').style = "display: none;";
    document.getElementById('stats-view').style = "display: block;";

    highlight_label('stats');
    reset_content_height();

    window.history.pushState(window.history.state, 'Stats');
    window.history.state = 'stats';

    stats_socket = new WebSocket("ws://" + document.domain + ":5000/stats");
    stats_socket.onopen = function (event) {
        stats_socket.send(get_token()); 
    };
    stats_socket.onmessage = function (event) {
        var data = JSON.parse(event.data);
        draw_charts(data);
    };
    stats_socket.onclose = function (event) {
        console.log('closed data socket', event);
    };
    stats_socket.onerror = function (event) {
        console.log('error data socket', event);
    };
});

// in any other case
page('*', function(){
    page('/');
});

// calculates SHA3 hash to use for password hashing on client-side
hash = function(str) {
    return CryptoJS.SHA3(str).toString();
}

var users_chart, posts_chart; 
draw_charts = function(d) {
    if (!document.getElementById("users-chart") || !document.getElementById("posts-chart"))
        return;

    var users_ctx = document.getElementById("users-chart").getContext("2d");
    var posts_ctx = document.getElementById("posts-chart").getContext("2d");

    if (users_chart)
        users_chart.destroy();
    if (posts_chart)
        posts_chart.destroy();

    // chart with users' info
    var data = {
        labels: ["Online", "Registered"],
        datasets: [{
                    fillColor: "#F7464A",
                    highlightFill: "#FF5A5E",
                    data: [d['online'], d['all_users']]
                    }
                ]
    };
    users_chart = new Chart(users_ctx).Bar(data);

    // chart with number of posts
    data = {
        labels: ["Your", "All"],
        datasets: [{
                    fillColor: "#583DDF",
                    highlightFill: "#6553BF",
                    data: [d['posts'], d['all_posts']]
                    }
                ]
    };

    posts_chart = new Chart(posts_ctx).Bar(data);
    document.getElementById("users-chart").innerHTML = '';
    document.getElementById("posts-chart").innerHTML = '';
}

/* calculating Hash-based message authentication code.
   message consists from values of all sending parameters(concatenated in 
   order of alphanumerical order of keys), secret key and timestamp
*/
hash_message = function(data) {
    var key = get_secret();

    var timestamp = Math.floor(Date.now() / 1000);
    // due to different json formating of the string in js and python
    // gathering only values in a row
    var message = '';
    for (var prop of Object.keys(data).sort()) {
        message += data[prop];
    }
    message += timestamp.toString();

    return {'hash': CryptoJS.HmacSHA1(message, key).toString(),
            'timestamp': timestamp};
}

ajax_call = function(method, path, func, data) {
    url = "http://" + document.domain + ':5000';

    var xhttp = new XMLHttpRequest();

    xhttp.onreadystatechange = function() {
        if (xhttp.readyState == 4 && xhttp.status == 200) {

            var resp = JSON.parse(xhttp.responseText);

            func(resp);

            console.log(JSON.parse(xhttp.responseText));
        }
    };

    xhttp.open(method, url + path, true);

    if (method == 'GET')
        xhttp.send();
    else {
        xhttp.setRequestHeader("Content-Type", "application/json");

        // when log in or sign up - sending without hash
        if (path != "/sign_in" && path != "/sign_up") {
            var mes_hash = hash_message(data);
            var data_with_hash = {'data': data, 'hash': mes_hash['hash'],
                                  'timestamp': mes_hash['timestamp']};

            xhttp.send(JSON.stringify(data_with_hash));
        }
        else
            xhttp.send(JSON.stringify(data));
    }
}

window.onload = function(){
    if (localStorage.getItem('token'))
        display_view('profileview');
    else
        display_view('welcomeview');
    page.start();
}

// defining all action-functions, which are not displayed by default
define_onclick_functions = function() {
    var account_tab = document.getElementById("account-tab");
    account_tab.onclick = function() {
        page('/account');
    }

    var home_tab = document.getElementById("home-tab");
    home_tab.onclick = function() {
        page('/home')
    }

    var browse_tab = document.getElementById("browse-tab");
    browse_tab.onclick = function() {
        page('/browse');
    }

    var stats_tab = document.getElementById("stats-tab");
    stats_tab.onclick = function() {
        page('/stats');
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
    refresh_button_browse.onclick = function() {
        var email_found = document.getElementById("search-field").value;

        refresh_wall('browse', email_found);
    }

    var signout_button = document.getElementById("sign-out");
    signout_button.onclick = function() {
        signout();
    }

    var search_button = document.getElementById("search-send");
    search_button.onclick = function() {
        search_method();
    }
}

display_view = function(view) {
    if (document.getElementById('view'))
        document.getElementById('view').innerHTML = document.getElementById(view).innerHTML;
    else {
        var new_view = document.createElement("div");
        var att = document.createAttribute("id");
        att.value = "view";
        new_view.setAttributeNode(att);
        
        document.body.appendChild(new_view);

        document.getElementById('view').innerHTML = document.getElementById(view).innerHTML;
    }

    if (view == 'welcomeview') {
        document.getElementsByTagName("body")[0].style.background = "#6699ff";
    }
    if (view == 'profileview') {
        define_onclick_functions();
        document.getElementsByTagName("body")[0].style.background = "#FFF";
    }
}

display_error_msg = function(id, msg) {
    document.getElementById(id).innerHTML = msg;

    // forcing to disappear notification after 3 seconds
    setTimeout(function() {
                document.getElementById(id).innerHTML = '';
                }, 3000);
}

/* checking correctness of entered data. passwords must match and be
   longer than 8 symbols
*/
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

    display_error_msg("error-reg", msg);

    return status;
}


// implementing Diffie–Hellman key exchange
compute_public_key = function() {
    // own secret value between 0 and 10
    var x = Math.floor((Math.random() * 10));

    var public_key = Math.pow(g, x) % p;
    var key = {'public_key': public_key, 'secret_variable': x};

    return key;
}

compute_secret_key = function(server_public, x) {
    return Math.pow(parseInt(server_public), x) % p;
}

login = function(email, password) {
    var key = compute_public_key();

    var data = {'email': email, 'password': password, 'public_key': key['public_key']};

    func = function(resp) {
        if (!resp.success) 
            display_error_msg("error-log", resp.message);
        else {
            var secret_key = compute_secret_key(resp.key, key['secret_variable']);
            localStorage.setItem('secret', secret_key);

            localStorage.setItem('token', resp.data);

            display_view('profileview');
            page('/account');


            /* socket init after successful login, to which is sended information about 
            session termination when user is logged from another browser
            */
            var login_socket;
            login_socket = new WebSocket("ws://" + document.domain + ":5000/sock");
            login_socket.onopen = function (event) {
                login_socket.send(email); 
            };
            login_socket.onmessage = function (event) {
                if (event.data == "bye") {
                    login_socket.close();
                    signout(true);
                }
            };
            login_socket.onclose = function (event) {
                console.log('closed socket', event);
            };
            login_socket.onerror = function (event) {
                console.log('error', event);
            };

        }
    }

    ajax_call("POST", "/sign_in", func, data);
}

login_form = function() {
    var form = document.forms['login-form'];
    var email = form['email'].value;
    var password = hash(form['pass'].value);

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
        password: hash(form['pass'].value)
    };


    if (check_reg_correctness()) {
        func = function(resp) {
        	if (!resp.success)
                display_error_msg("error-reg", resp.message);
        	else
        		login(data.email, data.password);
        }

        ajax_call("POST", "/sign_up", func, data);
    }
}

signout = function(forced) {
    var data = {'token': get_token()};

    if (forced)
        data['forced'] = true;

    ajax_call("POST", "/sign_out", function(){}, data);

    localStorage.removeItem('token');
    localStorage.removeItem('secret');

    display_view('welcomeview');
    page('/');
}

search_method = function() {
    var email = document.getElementById("search-field").value;
    
    func = function(resp) {
        if (!resp.success) 
            display_error_msg("search-error", resp.message);
        else 
            show_profile(resp.data);
    }

    ajax_call("GET", "/get_user_data_by_email?token="+get_token()+"&email="+email,
                func);
}

send_button = function(where) {
        var msg = document.getElementById("status-field-" + where).value;
        var token = get_token();

        if (where == 'home')
            var email = get_user_info().email;
        else if (where == 'browse')
            var email = document.getElementById("search-field").value;

        var data = {'token': token, 'message': msg, 'email': email};

        func = function(resp) {
            if (resp.success) {
                document.getElementById("status-field-" + where).value = '';
                refresh_wall(where, email);
            }
        }

        ajax_call("POST", "/post_message", func, data);
    }


refresh_wall = function(which, email) {

    func = function(resp) {
        if (resp.success) {
            document.getElementById("wall-list" + '-' + which).innerHTML = ''

            var messages = resp.data;

            for (var msg of messages)
                append_message_li(which, msg);
            
            prolonging_content(which);
        }
    }
    
    if (which == 'home')
        ajax_call("POST", "/get_user_messages_by_token", func, {'token': get_token()});
    else if (which == 'browse')
        ajax_call("POST", "/get_user_messages_by_email", func, 
                  {'email': email, 'token': get_token()});
}

append_message_li = function(which_wall, msg) {
    var newLi = document.createElement("li");
    if (msg.media) {
        if (msg.content.slice(-3) == "mp4") {
            var text = document.createElement("video");
            text.setAttribute("width", "360");
            text.setAttribute("height", "240");
            text.setAttribute("controls", "true");

            var src = document.createElement("source");
            src.setAttribute("src", "media/" + msg.content);
            src.setAttribute("type", "video/mp4");

            text.appendChild(src);
        }
        else {
            var text = document.createElement("img");
            text.setAttribute("src", "media/" + msg.content);
            text.setAttribute("width", "360");
            text.setAttribute("height", "240");
        }
    }
    else
        var text = document.createTextNode('"' + msg.content + '" from ' + msg.writer);

    newLi.appendChild(text);
    var ulnew = document.getElementById("wall-list-" + which_wall);
    ulnew.appendChild(newLi); 
}
// function which prolongs height of the content part(places border for it lower, if needed)
prolonging_content = function(where) {
    var att = document.createAttribute("style");
    att.value = "height: " + (400 + parseInt(window.getComputedStyle(document.getElementById("wall-" + where)).height)).toString() + "px;";
    document.getElementById("content").setAttributeNode(att);
}
// resets height of content part to default value
reset_content_height = function() {
    var att = document.createAttribute("style");
    att.value = "height: 550px";
    document.getElementById("content").setAttributeNode(att);
}

// obtains token from localstorage
get_token = function() {
    return localStorage.getItem('token');
}
// obtains secret key from localstorage
get_secret = function() {
    return localStorage.getItem('secret');
}

get_user_info = function() {
    token = get_token();

    url = "http://" + document.domain + ':5000';

    var xhttp = new XMLHttpRequest();

    xhttp.open("GET", url + "/get_user_data_by_token?token="+token, false);

    xhttp.send();

    if (xhttp.readyState == 4 && xhttp.status == 200) {

            var resp = JSON.parse(xhttp.responseText);

            return resp.data;

            console.log(JSON.parse(xhttp.responseText));
    }

}

// makes selected tab label more notable
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


fill_user_info_fields = function(tab, info) {
    document.getElementById(tab + '-email').innerHTML = info.email;
    document.getElementById(tab + '-firstname').innerHTML = info.firstname;
    document.getElementById(tab + '-familyname').innerHTML = info.familyname;
    document.getElementById(tab + '-gender').innerHTML = info.gender;
    document.getElementById(tab + '-city').innerHTML = info.city;
    document.getElementById(tab + '-country').innerHTML = info.country;
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
        document.getElementById('change-error').style.color = "FF0000";
        display_error_msg("change-error", error_msg);
        return false;
    }

    var data = {'token': get_token(), 'old_password': hash(current), 
                'new_password': hash(pass1)};

    func = function(resp) {
        if (!resp.success) {
            document.getElementById('change-error').style.color = "FF0000";
            display_error_msg("change-error", resp.message);
        }
        else {
            document.getElementById('change-error').style.color = "00FF00";
            display_error_msg("change-error", resp.message);
            document.getElementById("pass-change-form").reset();
        }
    }

    ajax_call("POST", "/change_password", func, data);

}

show_profile = function(data) {
    document.getElementById('search-content').style = "display: none;";
    document.getElementById('profile-unfam').style = "display: block;";
    fill_user_info_fields('browse', data);
    refresh_wall('browse', data.email);
}



// for drag&drop part:
drag_and_drop = function(){ 
    var holder = document.getElementById('holder'),
        tests = {
          filereader: typeof FileReader != 'undefined',
          dnd: 'draggable' in document.createElement('span'),
          formdata: !!window.FormData,
          progress: "upload" in new XMLHttpRequest
        }, 
        support = {
          filereader: document.getElementById('filereader'),
          formdata: document.getElementById('formdata'),
          progress: document.getElementById('progress')
        },
        acceptedTypes = {
          // 'image/png': true,
          // 'image/jpeg': true,
          // 'image/gif': true
        },
        progress = document.getElementById('uploadprogress'),
        fileupload = document.getElementById('upload');

    "filereader formdata progress".split(' ').forEach(function (api) {
      if (tests[api] === false) {
        support[api].className = 'fail';
      } else {
        // FFS. I could have done el.hidden = true, but IE doesn't support
        // hidden, so I tried to create a polyfill that would extend the
        // Element.prototype, but then IE10 doesn't even give me access
        // to the Element object. Brilliant.
        support[api].className = 'hidden';
      }
    });

    function previewfile(file) {
      if (tests.filereader === true && acceptedTypes[file.type] === true) {
        var reader = new FileReader();
        reader.onload = function (event) {
          var image = new Image();
          image.src = event.target.result;
          image.width = 300; // a fake resize
          image.height = 30; // a fake resize
          holder.appendChild(image);
        };

        reader.readAsDataURL(file);
      }  else {
        holder.innerHTML += '<p>Uploaded ' + file.name + ' ' + (file.size ? (file.size/1024|0) + 'K' : '');
        console.log(file);
      }
    }

    function readfiles(files) {
        var formData = tests.formdata ? new FormData() : null;
        for (var i = 0; i < files.length; i++) {
          if (tests.formdata) formData.append('file', files[0]);
          previewfile(files[i]);
        }

        // now post a new XHR request
        if (tests.formdata) {
          var xhr = new XMLHttpRequest();
          xhr.open('POST', 'http://127.0.0.1:5000/upload');
          xhr.onload = function() {
            refresh_wall("home");
            progress.value = progress.innerHTML = 100;
          };

          if (tests.progress) {
            xhr.upload.onprogress = function (event) {
              if (event.lengthComputable) {
                var complete = (event.loaded / event.total * 100 | 0);
                progress.value = progress.innerHTML = complete;
              }
            }
          }

          formData.append('token', get_token());

          console.log(formData);
          xhr.send(formData);
        }
    }

    if (tests.dnd) { 
      holder.ondragover = function () { this.className = 'hover'; return false; };
      holder.ondragend = function () { this.className = ''; return false; };
      holder.ondrop = function (e) {
        this.className = '';
        e.preventDefault();
        readfiles(e.dataTransfer.files);
      }
    } else {
      fileupload.className = 'hidden';
      fileupload.querySelector('input').onchange = function () {
        readfiles(this.files);
      };
    }
}