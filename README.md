# Decentralized Crawler - GoogleMap Cafe info

### Description
A decentralized crawler which targets to crawl GoogleMap cafe data (shop information). <br>
<br>

### Motivation
This program be developed for my responsibility of crawling data from internet. It's a part of side project which also be called as "Coffee Google" currently. <br>
For "Coffee Google" project, it needs to integrate all data which from different sources and must to crawl data from internet. However, general crawler program is too slow to get target data, especially crawler program be developed with framework Selenium. <br>
<br>

### Skills
This project classifies it to 2 parts. One is crawler, another one is other prcesses logic-implements (like Multiple Actors relationship, Send message mechanism and build Kafka producer, consumer, etc). <br>

#### Environment
##### For Developing
OS: MacOS (Current Version: 10.14.5)

#### For Running
OS: MacOS (Current Version: 10.14.5), Windows OS (Current Version: Win10)

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

In this project, everything depends on one thing --- AKKA to build crawler code to be a decentralized system. However, this project builded a stand-alone mode code currently. Below is the AKKA actors tree architecture in this project. <br>
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
Build workers and distribute job to them to work. It has 3 different worker leaders here:
  * Crawl Paladin <br>
  Build and manage crawl soldiers. This project divides the targert crawl-content to 4 parts and 4 different paladins have responsibility of them.
    * Cafe basic information
    * Cafe services
    * Cafe comments
    * Cafe images
  
  * Pre-Data Producer Paladin <br>
  Receive the Pre-Data from King (master) and distribute to workers. <br>
  
  * Data-Saver Paladin <br>
  Receive all data it gets from crawl soldiers and save it to database or files. <br>
  This Paladin is independence even it doesn't have any Soldiers be built under it because its main job is integrating all of data which be send by all "Crawl Soldiers" in any time (immediatelly). In other words, it guarantees the connector session is unique between database and multiple actors. <br>
  

* Workers (Soldiers) <br>
Receive task and essentailly work the content. It has 3 different workers: <br>
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

Kafka is a one of greatest software product! Kafka broken be a very important role in this project, that's "Distributer". Please refer to the below AKKA with Kafka Relationship <br>
<br>

![](https://github.com/Chisanan232/Decentralized-Crawler---GoogleMap-Cafe-info/raw/master/docs/imgs/GoogleMap_Cafe_Decentralized_Crawler_Diagram-Kafka_Diagram.png)

<br>

The project let King to be the all actors management and Paladins to be the management and "Distributer" (Paladin also is but it's a little bit different with Kafka, let us talk about it later). Some soldiers which be build up by Paladins is the "Kafka Role". "Pre-Data Soldiers" is Kafka Producer and "Search Soldier" is Kafka Consumer. <br>
First, "Search Soldier" will keep consuming the message even it has nothing in topic. If it gets something, "Search Soldier" sends it to "Crawl Soldier" as AKKA actor message immediately. For "Pre-Data Soldier" part, it starts to receive task content (Pre-Data) and produces it to target topic which be sniffed by "Search Soldier" until finishes the data. <br>

#### Addition of "Distributer"
In Kafka "Distributer" point, it for Kafka consumers. But in AKKA actor role Paladin "Distributer", it for distributing data to multiple AKKA actor role Soldier (Pre-Data Paladin) or build up multiple AKKA actors to do something (All Paladin except Data-Saver Paladin). The distribute objects between them are different.

#### Benefits
##### Re-Balance <br>
Kafka could auto-distribute the partitions of topic to consumers. Developer could set any number of consumers they want to receive target message and doesn't need to do other anything.

##### Data is Unique <br>
This is one of the most important features of Kafka. That helps developer deeply decrease development complexity.

##### Singler and Simplier Development <br>
In this project, no matter which type of Soldiers (Worker), it has responsibility of ONE and SIMPLE job. For example, "Search Soldier" (Kafka Consumer) target to sniff all message of target topic; "Pre-Data Soldier" (Kafka Producer) produce message (Crawl Pre-Data) which be assigned from Paladin. "Crawl Soldier" could pay attention to crawl data because "Search Soldier" could help it sniff and send Pre-Data message to it. Each of them has SIMPLE and CLEAR job to do.

<br>

#### Crawler Flow Chart

Here is the GoogleMap cafe crawler program flow chart which could help developer understand the full program process how to run and the software architecture.

<br>
 
![](https://github.com/Chisanan232/Decentralized-Crawler---GoogleMap-Cafe-info/raw/master/docs/imgs/GoogleMap_Cafe_Decentralized_Crawler_Diagram-Cafe_Crawler.png)
 
<br>

