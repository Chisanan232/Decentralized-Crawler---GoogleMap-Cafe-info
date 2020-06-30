package Cafe_GoogleMap_Crawler.src.main.scala.Soldier

import Cafe_GoogleMap_Crawler.src.main.scala.config._
import Cafe_GoogleMap_Crawler.src.main.scala.Basic

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
      WorkStatus.Working = true
//      val runningResult = context.parent.path.name.toString match {
//        case AkkaConfig.CafeBasicPaladinName =>  te.runCode(Basic, target)
//        case AkkaConfig.CafeServicePaladinName =>  te.runCode(Services, target)
//        case AkkaConfig.CafeCommentsPaladinName =>  te.runCode(Comments, target)
//        case AkkaConfig.CafeImagesPaladinName =>  te.runCode(Images, target)
//      }
      val runningResult = te.runCode(Basic, target)
      WorkStatus.Working = false

      // Get the result (cafe info in GoogleMap) and save it to database 'Cassandra'
      println(runningResult)
      // Send the data back to the Paladin to write to database
      context.parent ! RunningTaskResult("Here is the crawl-result data.", runningResult)

  }

}
