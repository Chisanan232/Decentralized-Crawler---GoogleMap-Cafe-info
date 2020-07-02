# Decentralized Crawler - GoogleMap Cafe info
<br>
### Description
A decentralized crawler which target to crawl GoogleMap cafe data (shop information). <br>
<br>
<br>
### Motivation
This project exist for my side project about ... maybe you should think it like "Coffee Google". <br>
We need to integrate all data which from different sources and must to crawl data from internet. <br>
However, general crawler is too slow to get target data we want, especially we crawl data with Selenium. <br>
<br>
<br>
### Skills
For this project, it be classified 2 parts. One is crawler, another one is other prcesses logic-implements (like Multiple Actors relationship, Send message mechanism and build Kafka producer, consumer, etc). <br>
<br>
#### Crawler
Language: Python <br>
Version: 3.7 up <br>
Framework: Requests, Selenium <br>
<br>
#### All other logic-Implements
Language: Scala <br>
Version: 2.12 <br>
Framework: Spark (version: 2.4.5), AKKA (version: 2.4.20) <br>
Message Queue Server: Kafka (version: 2.5.0) <br>
Databsase: Cassandra (Datastax driver-core version: 3.6.0, Spark connector version: 2.5.0) <br>
<br>
<br>
### AKKA Actors Tree Relationsahip 
 <br>
In this project, no matter what thing you want to do, all things, al logic-implements base on one thing --- AKKA. Why? Because you want to build your code to be a decentralized system, right? So we need to use AKKA feature to do this. However, before we do that, let us build a stand-alone mode code first. Below is the AKKA actors tree architecture we use in the project. <br>
 <br>
 
![](https://github.com/Chisanan232/Decentralized-Crawler---GoogleMap-Cafe-info/raw/master/docs/imgs/GoogleMap_Cafe_Decentralized_Crawler_Diagram-Akka_Actors_Tree.png)
 
 <br>

Actors Tree Relationship like: <br>
Master (King) ---> Worker Leaders (Paladins) ---> Workers (Soldiers) <br>
 <br>
* Master (King) <br>
The boss of all actors. It builds and manages worker leaders, also, it get the pre-data in the prestart status.
  * Import Pre-data
  * Build worker leaders and send task to let them ready to stand by (wait for pre-data).


* Worker Leaders (Paladins) <br>
Build workers and distribute job to them to work. And it has 3 different worker leaders here:
  * Crawl Paladin
  Build and manage crawl soldiers. In this project, we divide the content part to 4 parts and 4 different paladins have responsibility of them.
    * Cafe basic information
    * Cafe services
    * Cafe comments
    * Cafe images <br>
  
  * Pre-Data Producer Paladin <br>
  Receive the Pre-Data from King (master) and distribute to workers. <br>
  
  * Data-Saver Paladin <br>
  Receive all data we got from crawl soldiers and save it to database or files.  <br>
  

* Workers (Soldiers) <br>
Receive task and essentailly work the content. Here we also has 3 different workers: <br>
  * Crawl Soldier <br>
  Receive task (from Search Soldiers) and crawl data.  <br>
  
  * Pre-Data Preoducer Soldier <br>
  Receive task and Pre-Data and write it into Kafka broken. <br> 
  This soldier is Kafka Producer. <br>
  
  * Search Soldier <br>
  Be activated by King firt and keep sniffing (consuming) target Topic of Kafka. If it get something, send it to every soldiers who has responsibility of different content part. If it doesn't, on going to keep listening.  <br>
  This soldier is Kafak Consumer. <br>



### AKKA with Kafka Relationship 

Kafka is a one of greatest software product! Why we choice it to use in this project?  <br>


