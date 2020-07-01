package Cafe_GoogleMap_Crawler.src.main.scala

import Cafe_GoogleMap_Crawler.src.main.scala.config._
import Cafe_GoogleMap_Crawler.src.main.scala.King.CafeKing

import akka.actor.{ActorSystem, Props}


object CafeCrawlerMain extends App {

  val system = ActorSystem(AkkaConfig.SystemName)
  val kingActor = system.actorOf(Props[CafeKing], AkkaConfig.CafeKingName)
  kingActor ! CrawlTarget("", "")

}
