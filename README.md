Web server
=====================

Simple python http server build on sockets. It's based on TCP server. Each connection is running in the unique thread.

Testing results with Apache Bench with 5 workers:
```bash
Server Software:        Python-WebServer
Server Hostname:        localhost
Server Port:            80

Document Path:          /
Document Length:        34 bytes

Concurrency Level:      100
Time taken for tests:   269.497 seconds
Complete requests:      50000
Failed requests:        1328
   (Connect: 0, Receive: 331, Length: 997, Exceptions: 0)
Keep-Alive requests:    0
Total transferred:      8624528 bytes
HTML transferred:       1666102 bytes
Requests per second:    185.53 [#/sec] (mean)
Time per request:       538.993 [ms] (mean)
Time per request:       5.390 [ms] (mean, across all concurrent requests)
Transfer rate:          31.25 [Kbytes/sec] received

Connection Times (ms)
              min  mean[+/-sd] median   max
Connect:        0    1  11.1      0    1464
Processing:     0  508 4930.7      5   76644
Waiting:        0  240 2713.9      5   75752
Total:          0  509 4930.8      5   76645

Percentage of the requests served within a certain time (ms)
  50%      5
  66%      6
  75%      7
  80%      8
  90%     11
  95%     21
  98%   3739
  99%  10018
 100%  76645 (longest request)
```

## How to
Python >= 3.7 is required. Run server in terminal with the following command:
```bash
$ python httpd.py -s <server host> -p <server port> -w <number of connections> -r <root folder with files to serve>
```
