package Cafe_GoogleMap_Crawler.src.main.scala

sealed trait CrawlPart

case object Basic extends CrawlPart
case object Services extends CrawlPart
case object Comments extends CrawlPart
case object Images extends CrawlPart
case object All extends CrawlPart
