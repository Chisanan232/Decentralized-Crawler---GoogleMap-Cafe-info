# Decentralized Crawler - GoogleMap Cafe info

### Description
A decentralized crawler which targets to crawl GoogleMap cafe data (shop information). <br>
<br>

### Motivation
This program for my responsibility of crawling data from internet. It's a part of side project about ... maybe you could think it like "Coffee Google". <br>
We need to integrate all data which from different sources and must to crawl data from internet. However, general crawler program is too slow to get target data we want, especially crawler program be developed with framework Selenium. <br>
<br>

### Skills
For this project, I classify it to 2 parts. One is crawler, another one is other prcesses logic-implements (like Multiple Actors relationship, Send message mechanism and build Kafka producer, consumer, etc). <br>

#### Crawler
Language: Python <br>
Version: 3.7 up <br>
Framework: Requests, Selenium <br>

#### All other logic-Implements
Language: Scala <br>
Version: 2.12 <br>
Framework: Spark (version: 2.4.5), AKKA (version: 2.4.20) <br>
Message Queue Server: Kafka (version: 2.5.0) <br>
Databsase: Cassandra (Datastax driver-core version: 3.6.0, Spark connector version: 2.5.0) <br>
<br>

### AKKA Actors Tree Relationsahip 

In this project, no matter what thing you want to do, all things, all logic-implements base on one thing --- AKKA. Why? Because you want to build your code to be a decentralized system. So we need to use AKKA feature to do this. However, before we do that, let us build a stand-alone mode code first. Below is the AKKA actors tree architecture we use in the project. <br>
 <br>
 
![](https://github.com/Chisanan232/Decentralized-Crawler---GoogleMap-Cafe-info/raw/master/docs/imgs/GoogleMap_Cafe_Decentralized_Crawler_Diagram-Akka_Actors_Tree.png)
 
 <br>

Actors Tree Relationship like: <br>
Master (King) ---> Worker Leaders (Paladins) ---> Workers (Soldiers) <br>
 <br>
* Master (King) <br>
The boss of all actors. It builds and manages worker leaders, also, it gets the pre-data in the prestart actor status.
  * Import Pre-data
  * Build worker leaders and send task to let them ready to stand by (wait for pre-data).


* Worker Leaders (Paladins) <br>
Build workers and distribute job to them to work. And it has 3 different worker leaders here:
  * Crawl Paladin <br>
  Build and manage crawl soldiers. In this project, we divide the content part to 4 parts and 4 different paladins have responsibility of them.
    * Cafe basic information
    * Cafe services
    * Cafe comments
    * Cafe images
  
  * Pre-Data Producer Paladin <br>
  Receive the Pre-Data from King (master) and distribute to workers. <br>
  
  * Data-Saver Paladin <br>
  Receive all data we got from crawl soldiers and save it to database or files. <br>
  This Paladin is independence even it doesn't have any Soldiers be built under it because its main job is integrating all of data which be send by all "Crawl Soldiers" in any time (immediatelly). In other words, it guarantee the connector session is unique between database and multiple actors. <br>
  

* Workers (Soldiers) <br>
Receive task and essentailly work the content. Here we also has 3 different workers: <br>
  * Crawl Soldier <br>
  Receive task (from Search Soldiers) and crawl data.  <br>
  
  * Pre-Data Preoducer Soldier <br>
  Receive task and Pre-Data and write (produce) it into Kafka broken. <br> 
  This soldier is Kafka Producer. <br>
  
  * Search Soldier <br>
  Be activated by King firt and keep sniffing (consuming) target Topic of Kafka. If it gets something, Search Soldier sends it to every soldiers who has responsibility of different content part. If it doesn't, on going to keep listening.  <br>
  This soldier is Kafak Consumer. <br>

<br>

### AKKA with Kafka Relationship 

Understand AKKA Actors tree Relationship and design. Let's talk about AKKA with Kafka Relationship. Kafka is a one of greatest software product! Why we choice it to use in this project? Kafka broken be a very important role here, that's "Distributer". Please refer to the below AKKA with Kafka Relationship <br>
<br>
 
![](https://github.com/Chisanan232/Decentralized-Crawler---GoogleMap-Cafe-info/raw/master/docs/imgs/GoogleMap_Cafe_Decentralized_Crawler_Diagram-Kafka_Diagram.png)
 
<br>

We let King to be the all actors management and Paladins to be the management and "Distributer" (Paladin also is but it's a little bit different with Kafka, let us talk about it later). Some soldiers which be build up by Paladins is the "Kafka Role". "Pre-Data Soldiers" is Kafka Producer and "Search Soldier" is Kafka Consumer. <br>
First, "Search Soldier" will keep consuming the message even it has nothing in topic. If it gets something, "Search Soldier" sends it to "Crawl Soldier" as AKKA actor message immediately. For "Pre-Data Soldier" part, it starts to receive task content (Pre-Data) and produces it to target topic which be sniffed by "Search Soldier" until finishes the data. <br>

#### Addition of "Distributer"
In Kafka "Distributer" point, it for Kafka consumers. But in AKKA actor role Paladin "Distributer", it for distribute data to multiple AKKA actor role Soldier (Pre-Data Paladin) or build up multiple AKKA actors to do something (All Paladin except Data-Saver Paladin). The distribute objects between them are different.

#### Benefits
##### Re-Balance <br>
Kafka could auto-distribute the partitions of topic to consumers. You could set any number of consumers you want to receive target message and don't need to do other anything.

##### Data is Unique <br>
I think this is the most important feature of Kafka. That's help developer deeply decrease development complexity.

##### Singler and Simplier Development <br>
You could find that no matter which one type of Soldiers (Worker), it has responsibility of ONE and SIMPLE job. For example, "Search Soldier" (Kafka Consumer) target to sniff all message of target topic; "Pre-Data Soldier" (Kafka Producer) produce message (Crawl Pre-Data) which be assigned from Paladin. "Crawl Soldier" could pay attention to crawl data because "Search Soldier" could help it sniff and send Pre-Data message to it. Each of them has SIMPLE and CLEAR job to do.

<br>

#### Crawler Flow Chart

Here is the GoogleMap cafe crawler program flow chart. You could understand the full program process how to run and the software architecture.

<br>
 
![](https://github.com/Chisanan232/Decentralized-Crawler---GoogleMap-Cafe-info/raw/master/docs/imgs/GoogleMap_Cafe_Decentralized_Crawler_Diagram-Cafe_Crawler.png)
 
<br>

