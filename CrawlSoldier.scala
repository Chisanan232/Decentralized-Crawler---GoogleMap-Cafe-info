package Cafe_GoogleMap_Crawler

import akka.actor.{Actor, ActorLogging}


class CrawlSoldier extends Actor with ActorLogging {

  var SoldierID: Int = 0

  override def receive: Receive = {

    case ReadyOnStandby(content, soldierID) =>
      log.info("Copy that! Ready on stand by!")
      this.SoldierID = soldierID


    case CrawlTask(content, target) =>
      log.info("Get the crawler pre-data!")

      // Parse the crawl pre-data.
      val id = target.get("id")
      val api = target.get("url")
      val lat = target.get("lat")
      val lng = target.get("lng")

      // Start to crawl target data with the info.
      val te = new TasksExecutor

  }

}
