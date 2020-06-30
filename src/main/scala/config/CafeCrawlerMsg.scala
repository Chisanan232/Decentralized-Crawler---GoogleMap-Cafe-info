package Cafe_GoogleMap_Crawler.src.main.scala.config

import Cafe_GoogleMap_Crawler.src.main.scala.CrawlPart

trait CafeCrawlerMsg {
  val content: String
}


// System
case class CrawlTarget(content: String, part: String) extends CafeCrawlerMsg


// King
case class CallCafeBasicPaladin(content: String) extends CafeCrawlerMsg
case class CallCafeServicesPaladin(content: String) extends CafeCrawlerMsg
case class CallCafeCommentsPaladin(content: String) extends CafeCrawlerMsg
case class CallCafeImagesPaladin(content: String) extends CafeCrawlerMsg
case class CallDataSaverPaladin(content: String) extends CafeCrawlerMsg

case class CrawlCafeBasic(content: String) extends CafeCrawlerMsg
case class CrawlCafeServices(content: String) extends CafeCrawlerMsg
case class CrawlCafeComments(content: String) extends CafeCrawlerMsg
case class CrawlCafeImages(content: String) extends CafeCrawlerMsg

//case class DistributePreData(content: String, cafeIDs: List[Any], cafeAPIs: List[Any], cafeLats: List[Any], cafeLngs: List[Any]) extends CafeCrawlerMsg
case class DistributePreData(content: String, cafeDataNum: Int, cafePreData: List[Any]) extends CafeCrawlerMsg

case class SearchPreData(content: String, soldierID: Int) extends CafeCrawlerMsg


// Paladins
case class ReadyOnStandby(content: String, soldierID: Int) extends CafeCrawlerMsg
// Distribute Pre-Data Paladin
//case class ImportCafeCrawlerConditions(content: String, cafeIDs: List[Any], cafeAPIs: List[Any], cafeLats: List[Any], cafeLngs: List[Any]) extends CafeCrawlerMsg
case class ImportCafeCrawlerConditions(content: String, cafePreData: List[Any]) extends CafeCrawlerMsg


// Basic Paladin

// Services Paladin


// Comments Paladin


// Images Paladin


// Pre-Data Soldiers
case class ProduceFinish(content: String) extends CafeCrawlerMsg


// Search Soldiers
case class CrawlTask(content: String, target: Map[String, String]) extends CafeCrawlerMsg


// Crawler Soldiers
case class RunningTaskResult(content: String, part: CrawlPart, data: String) extends CafeCrawlerMsg


// For test or debug
case class DebugMsg(content: String) extends CafeCrawlerMsg
