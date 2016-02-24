# twidder
Simple SPA as assignment for TDDD97 course  

[Link for tasks](http://www.ida.liu.se/~TDDD97/labs/index.en.shtml#assig)

To start the server run:  

`gunicorn -k flask_sockets.worker runserver:app -b 0.0.0.0:5000 -D`
