const ws = new WebSocket('ws://localhost:8080');

ws.onopen = () => {
  console.log('connected');
  document.getElementById('loginError').style.color = 'green';
  document.getElementById('loginError').innerHTML = 'Connected to server'
  document.getElementById('signupError').style.color = 'green';
  document.getElementById('signupError').innerHTML = 'Connected to server'
  if(dev){
    ping();
  }
};

ws.onclose = () => {
  console.error('disconnected');
  document.getElementById('loginError').style.color = 'red';
  document.getElementById('loginError').innerHTML = 'Disconnected from server'
  document.getElementById('signupError').style.color = 'red';
  document.getElementById('signupError').innerHTML = 'Disconnected from server'
};

ws.onerror = error => {
  document.getElementById('loginError').style.color = 'red';
  document.getElementById('loginError').innerHTML = 'Unable to connect to server'
  document.getElementById('signupError').style.color = 'red';
  document.getElementById('signupError').innerHTML = 'Unable to connect to server'
  console.error('failed to connect', error);
};

ws.onmessage = event => {
    let cutMessage = event.data.split('~')
    switch(cutMessage[0]){
        case 'test':
            console.log(cutMessage[1])
            return;
        case 'broadcast':
            console.log('broadcasted ' + cutMessage[1])
            return;
        case 'signuperror':
            document.getElementById('signupError').style.color = 'red';
            document.getElementById('signupError').innerHTML = 'Username already exist'
            return;
        case 'signupsuccess':
            document.getElementById('signupError').style.color = 'green';
            document.getElementById('signupError').innerHTML = 'Signup successful. Login to continue (we have no recaptchas we only have ubatchas'
            return;
        case 'loginerror':
            document.getElementById('loginError').style.color = 'red';
            document.getElementById('loginError').innerHTML = 'Username or paassword is incorrect'
            return;
        case 'loginsuccess':
            document.getElementById('loginError').style.color = 'green';
            document.getElementById('loginError').innerHTML = 'loading...'
            document.getElementById('loginButton').disabled = true;
            gameData = JSON.parse(cutMessage[1]);
            setTimeout(function(){
                update();
                document.getElementById('loginScreen').style.display = "none";
                document.getElementById('menuScreen').style.display = "block";
            },1000)
            return;
        case 'chat':
            document.getElementById('chatMessages').innerHTML += '<b>' + cutMessage[1] + '</b>' + cutMessage[2] + '<br>'
            return;
        case 'pong':
            pong();
            return;
        case 'what the hell happened?':
            console.log('oh god something happened')
            return;
        default:
            console.log('what the hell happened?')
            return;
    }
};