Web server
=====================

Simple python http server build on sockets. It's based on TCP server. Eash connection is running in the unique thread.

Testing results with Apache Bench:
```bash
Server Software:        Python-WebServer
Server Hostname:        0.0.0.0
Server Port:            80

Document Path:          /
Document Length:        0 bytes

Concurrency Level:      100
Time taken for tests:   278.063 seconds
Complete requests:      50000
Failed requests:        0
Non-2xx responses:      50000
Total transferred:      6600000 bytes
HTML transferred:       0 bytes
Requests per second:    179.82 [#/sec] (mean)
Time per request:       556.126 [ms] (mean)
Time per request:       5.561 [ms] (mean, across all concurrent requests)
Transfer rate:          23.18 [Kbytes/sec] received

Connection Times (ms)
              min  mean[+/-sd] median   max
Connect:        0  173 1196.6     66   21055
Processing:     3  367 1175.9    207   21156
Waiting:        3  326 1079.7    202   21150
Total:          4  540 1699.1    283   21258

Percentage of the requests served within a certain time (ms)
  50%    283
  66%    359
  75%    394
  80%    413
  90%    516
  95%    753
  98%   4765
  99%   7635
 100%  21258 (longest request)
```

## How to
Python >= 3.7 is required. Run server in terminal with the following command:
```bash
$ python httpd.py -s <server host> -p <server port> -w <number of connections> -r <root folder with files to serve>
```
