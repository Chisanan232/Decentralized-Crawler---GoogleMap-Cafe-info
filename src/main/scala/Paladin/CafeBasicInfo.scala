package Cafe_GoogleMap_Crawler.src.main.scala.Paladin

import Cafe_GoogleMap_Crawler.src.main.scala.config._
import Cafe_GoogleMap_Crawler.src.main.scala.Soldier.CrawlSoldier

import akka.actor.{Actor, ActorLogging, ActorRef, Props}

import org.apache.spark.{SparkConf, SparkContext}
import com.datastax.spark.connector._


class CafeBasicInfo extends Actor with ActorLogging {

  val conf = new SparkConf(true)
    .set("spark.cassandra.connection.host", CassandraConfig.CassandraHost)
    .setMaster(CassandraConfig.CassandraMaster)
    .setAppName(CassandraConfig.CassandraAppName)
  val sc = new SparkContext(conf)


  override def receive: Receive = {

    case CallCafeBasicPaladin =>
      log.info("I Receive task!")
      val consumerLeaderPath = context.self.path
      val msg = s"I'm ready! I'm $consumerLeaderPath"
      sender() ! msg


    case CrawlCafeBasic =>
      log.info("Got the Task! Start to crawl cafe basic information data.")

      val crawlerSoldiers = if (AkkaConfig.BasicCrawlerNumber.equals(0)) {
        new Array[ActorRef](AkkaConfig.CrawlerNumber)
      } else {
        new Array[ActorRef](AkkaConfig.BasicCrawlerNumber)
      }
      for (crawlerID <- 0.until(AkkaConfig.CrawlerNumber)) crawlerSoldiers(crawlerID) = context.actorOf(Props[CrawlSoldier], AkkaConfig.CafeBasicSoldierName + s"-$crawlerID")
      crawlerSoldiers.foreach(soldierRef => {
        val soldier = context.actorSelection(soldierRef.path)
        soldier ! ReadyOnStandby("Ready, soldiers! And here is your ID.", soldierRef.path.name.takeRight(1).toInt)
      })


    case RunningTaskResult =>
      log.info("Receive the crawl-result data!")

  }

}
