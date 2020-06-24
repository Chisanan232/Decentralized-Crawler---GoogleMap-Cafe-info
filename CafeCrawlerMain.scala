package Cafe_GoogleMap_Crawler

import akka.actor.{ActorSystem, Props}


object CafeCrawlerMain extends App {

  val system = ActorSystem("GoogleMapCafeCrawler")
  val kingActor = system.actorOf(Props[CafeKing], AkkaConfig.CafeKingName)
  kingActor ! CrawlTarget("", "")

}
