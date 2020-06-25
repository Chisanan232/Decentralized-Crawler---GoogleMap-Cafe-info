package Cafe_GoogleMap_Crawler

import org.apache.orc.impl.StringRedBlackTree
import scala.collection.JavaConverters._
import org.json4s.jackson.JsonMethods._
import org.json4s.DefaultFormats
import scala.concurrent.ExecutionContext.Implicits.global
import scala.util.{Success, Failure}
import scala.concurrent.duration._

import org.apache.kafka.clients.consumer.KafkaConsumer
import akka.actor.{Actor, ActorLogging}
import akka.util.Timeout


class SearchSoldier extends Actor with ActorLogging {

  var SoldierID: Int = 0

  override def receive: Receive = {

    case SearchPreData(content, soldierID) =>
      log.info("Roger that! Start to sniff all data of target topic og Kafka server.")
      this.SoldierID = soldierID

      implicit val groupID = "crawler-soldier"
      val cm = new DataConsumerManagement() {
        override def getMsg(timeoutMins: Int)(implicit consumer: KafkaConsumer[String, String]): Unit = {
          while (true) {
            val records = consumer.poll(timeoutMins).asScala
            for (record <- records) {
              if (record.value() != "" && record.value() != " ") {
                implicit val dataFormat = DefaultFormats
                val crawlPreData = parse(record.value().toString()).extract[Map[String, String]]

                // How to get the Akka actor by target actor'name
                // https://stackoverflow.com/questions/25966635/how-to-get-akka-actor-by-name-as-an-actorref
                implicit val timeout = Timeout(5.seconds)
                val king = AkkaConfig.CafeKingName
                val basicPaladin = AkkaConfig.CafeBasicPaladinName
                val basicSoldier = AkkaConfig.CafeBasicSoldierName
                context.system.actorSelection(s"user/$king/$basicPaladin/$basicSoldier-$soldierID").resolveOne().onComplete{
                  case Success(actorRef) => actorRef ! CrawlTask("Here is the crawl pre-data.", crawlPreData)
                  case Failure(ex) => log.error(s"The AKKA actor path 'user/$king/$basicPaladin/$basicSoldier-$soldierID' doesn't exist! Please check it again.")
                }
              }
            }
          }
        }
      }

      implicit val consumer = new KafkaConsumer[String, String](cm.defineProperties())
      cm.scanOnePartitionMsg(KafkaConfig.GoogleMapCrawlPreDataTopic, soldierID)
      cm.getMsg(100)

  }

}
