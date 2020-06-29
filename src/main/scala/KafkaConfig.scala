package Cafe_GoogleMap_Crawler

object KafkaConfig {

  val Nodes = ""

//  val GoogleMapCrawlPreDataTopic = "googlemap-crawl-pre-data"
//  val GoogleAPITopic = "GoogleMap-API"
//  val CafeLatTopic = "cafe-latitude"
//  val CafeLngTopic = "cafe-longitude"
//  val CafeIDTopic = "cafe-north-id"

  val GoogleMapCrawlPreDataTopic = "test-googlemap-crawl-pre-data"
  val GoogleAPITopic = "test-GoogleMap-API"
  val CafeLatTopic = "test-cafe-latitude"
  val CafeLngTopic = "test-cafe-longitude"
  val CafeIDTopic = "test-cafe-north-id"

  val GoogleMapCrawlPreDataTopicPartitionsNum = 2
  val GoogleAPITopicPartitionsNum = 2
  val CafeLatTopicPartitionsNum = 2
  val CafeLngTopicPartitionsNum = 2
  val CafeIDTopicPartitionsNum = 2

}
