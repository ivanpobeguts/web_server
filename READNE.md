Web server
=====================

Simple python http server build on sockets. It's based on TCP server. Eash connection is running in the unique thread.

Testing results with Apache Bench:
```bash
Server Software:        Python-WebServer
Server Hostname:        localhost
Server Port:            80

Document Path:          /
Document Length:        34 bytes

Concurrency Level:      100
Time taken for tests:   267.683 seconds
Complete requests:      50000
Failed requests:        0
Total transferred:      8800000 bytes
HTML transferred:       1700000 bytes
Requests per second:    186.79 [#/sec] (mean)
Time per request:       535.366 [ms] (mean)
Time per request:       5.354 [ms] (mean, across all concurrent requests)
Transfer rate:          32.10 [Kbytes/sec] received

Connection Times (ms)
              min  mean[+/-sd] median   max
Connect:        0  165 1082.6     59   17164
Processing:     4  368 1067.4    229   17375
Waiting:        4  357 1066.0    219   17374
Total:          5  533 1513.7    301   21445

Percentage of the requests served within a certain time (ms)
  50%    301
  66%    379
  75%    432
  80%    471
  90%    629
  95%    868
  98%   1746
  99%   9203
 100%  21445 (longest request)
```

## How to
Python >= 3.7 is required. Run server in terminal with the following command:
```bash
$ python httpd.py -s <server host> -p <server port> -w <number of connections> -r <root folder with files to serve>
```
