# Web URL Request Count using Hadoop MapReduce

## Objective
Count web requests received by each URL using Java and Hadoop MapReduce.

## Technologies
- Java 11
- Apache Hadoop 3.4.3
- HDFS and MapReduce

## Project Files
- src/ - Java Mapper, Reducer, and main class
- input/web_access_log.csv - Sample dataset
- show_results.sh - Displays results from HDFS
- mapred-site-local.xml - Local execution configuration

## Expected Output
/about      1
/contact    1
/home       4
/login      2
/products   2

## Note
Hadoop and HDFS must be configured on the computer running this project.
