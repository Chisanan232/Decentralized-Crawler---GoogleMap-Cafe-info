package Cafe_GoogleMap_Crawler.src.main.scala.config

import Cafe_GoogleMap_Crawler.src.main.scala.JsonFile

object AkkaConfig {

  var CrawlSaver = JsonFile

  val CrawlerNumber = 10
  val BasicCrawlerNumber = 0
  val ServicesCrawlerNumber = 0
  val CommentsCrawlerNumber = 0
  val ImagesCrawlerNumber = 0

  val SystemName = "GoogleMapCafeCrawler"

  val CafeKingName = "Cafe-King"
  val CafeDistributePaladinName = "Cafe-Distribute-Paladin"
  val CafeDataSaverPaladinName = "Cafe-Data-Saver-Paladin"
  val CafeBasicPaladinName = "Cafe-Basic-Paladin"
  val CafeServicePaladinName = "Cafe-Services-Paladin"
  val CafeCommentsPaladinName = "Cafe-Comments-Paladin"
  val CafeImagesPaladinName = "Cafe-Images-Paladin"

  val SearchPreDataSoldierName = "Search-PreData-Soldier"
  val ProduceCafePreDataSoldierName = "Cafe-Distribute-Soldier"
  val CafeBasicSoldierName = "Cafe-Basic-Soldier"
  val CafeServiceSoldierName = "Cafe-Services-Soldier"
  val CafeCommentsSoldierName = "Cafe-Comments-Soldier"
  val CafeImagesSoldierName = "Cafe-Images-Soldier"

}
