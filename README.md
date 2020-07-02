# Decentralized Crawler - GoogleMap Cafe info

### Description
A decentralized crawler which target to crawl GoogleMap cafe data (shop information). 


### Motivation
This project exist for my side project about ... maybe you should think it like "Coffee Google".
We need to integrate all data which from different sources and must to crawl data from internet. 
However, general crawler is too slow to get target data we want, especially we crawl data with Selenium.


### Skills
For this project, it be classified 2 parts. One is crawler, another one is other prcesses logic-implements (like Multiple Actors relationship, Send message mechanism and build Kafka producer, consumer, etc).

#### Crawler
Language: Python
Version: 3.7 up
Framework: Requests, Selenium

#### All other logic-Implements
Language: Scala
Version: 2.12
Framework: Spark (version: 2.4.5), AKKA (version: 2.4.20)
Message Queue Server: Kafka (version: 2.5.0)
Databsase: Cassandra (Datastax driver-core version: 3.6.0, Spark connector version: 2.5.0)

In this project, no matter what thing you want to do, all things, al logic-implements base on one thing --- AKKA. Why? Because you want to build your code to be a decentralized system, right? So we need to use AKKA feature to do this. However, before we do that, let us build a stand-alone mode code first. Below is the AKKA actors tree architecture we use in the project.

![](https://github.com/Chisanan232/Decentralized-Crawler---GoogleMap-Cafe-info/raw/master/docs/imgs/GoogleMap_Cafe_Decentralized_Crawler_Diagram-Akka_Actors_Tree.png)

