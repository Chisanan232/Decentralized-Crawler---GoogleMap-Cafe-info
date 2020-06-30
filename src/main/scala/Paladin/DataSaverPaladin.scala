package Cafe_GoogleMap_Crawler.src.main.scala.Paladin

import Cafe_GoogleMap_Crawler.src.main.scala.config._

import akka.actor.{Actor, ActorLogging}


class DataSaverPaladin extends Actor with ActorLogging {

  override def receive: Receive = {

    case RunningTaskResult(content, data) =>
      log.info("Receive the crawl-result data!")

  }

}
