#!/bin/bash
echo "===== URL Request Count Results ====="
$HADOOP_HOME/bin/hdfs dfs -cat /web_url_request_count/output/part-r-00000
