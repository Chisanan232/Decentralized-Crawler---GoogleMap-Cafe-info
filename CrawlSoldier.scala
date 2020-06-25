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

      // Start to crawl target data with the 'pre-data'.
      val te = new TasksExecutor
      te.runCode(Basic, target)

      // Get the result (cafe info in GoogleMap) and save it to database 'Cassandra'

  }

}
