package Cafe_GoogleMap_Crawler

import scala.util.parsing.json.JSONObject

import org.apache.kafka.clients.producer.KafkaProducer
import akka.actor.{Actor, ActorLogging, Props}


class ProducePreDataSoldier extends Actor  with ActorLogging {

  override def receive: Receive = {

    case ImportCafeCrawlerConditions(content, cafePreData) =>
      log.info("Roger that. Start to import data into Kafka server with target topic.")

      // 1. Convert data from Map to Json.
      // This is a shit method:
//      val preDataContent1 = (cafeIDs, cafeAPIs, cafeLats).zipped.toList
//      var preData1 = Map[String, Map[String, String]]()
//      for ((id, api, lat) <- preDataContent1) {
//        preData1 += (id.toString -> Map("API" -> api.toString, "Lat" -> lat.toString))
//      }
//
//      val preDataContent2 = (cafeIDs, cafeAPIs, cafeLngs).zipped.toList
//      var preData2 = Map[String, Map[String, String]]()
//      for ((id, api, lng) <- preDataContent2) {
//        val lat = preData1.get(id.toString).get.asInstanceOf[Map[String, String]].get("lat").get.toString
//        preData2 += (id.toString -> Map("API" -> api.toString, "Lat" -> lat, "Lng" -> lng.toString))
//      }
//
//      val jsonData = JSONObject(preData2)

      // This is a better method:
      // Do the data process in the Data Source Class with Spark.

      val pm = new DataProducerManagement
      implicit val producer = new KafkaProducer[String, String](pm.defineProperties())
      cafePreData.foreach(preData => {
        val jsonData = JSONObject(preData.asInstanceOf[Map[String, String]])
        pm.writeMsg(KafkaConfig.GoogleMapCrawlPreDataTopic, "Taipei", jsonData.toString())
      })
      pm.closeSession()
      context.parent ! ProduceFinish

  }

}
