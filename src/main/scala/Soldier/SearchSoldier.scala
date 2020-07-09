package Cafe_GoogleMap_Crawler.src.main.scala.Soldier

import Cafe_GoogleMap_Crawler.src.main.scala.config._
import Cafe_GoogleMap_Crawler.src.main.scala.CheckMechanism
import Cafe_GoogleMap_Crawler.src.main.scala.{CrawlPart, Basic, Services, Comments, Images}
import Cafe_GoogleMap_Crawler.src.main.scala.KafkaMechanism.DataConsumerManagement

import scala.concurrent.ExecutionContext.Implicits.global
import scala.concurrent.duration._
import scala.util.{Success, Failure}

import scala.collection.JavaConverters._
import scala.collection.mutable.ListBuffer
import org.json4s.jackson.JsonMethods._
import org.json4s.DefaultFormats

import org.apache.kafka.clients.consumer.KafkaConsumer
import akka.actor.{Actor, ActorLogging}
import akka.pattern.ask
import akka.util.Timeout


class SearchSoldier extends Actor with ActorLogging {

  private val check = new CheckMechanism
  var UnderWaitDataList = new ListBuffer[Map[String, String]]()

  var SoldierID: Int = 0

  private def parseData(data: Any): Map[String, String] = {
    implicit val dataFormat = DefaultFormats
    parse(data.toString()).extract[Map[String, String]]
  }

  private def getActorSelection(part: CrawlPart): (String, String) = {
    part match {
      case Basic => (AkkaConfig.CafeBasicPaladinName, AkkaConfig.CafeBasicSoldierName)
      case Services => (AkkaConfig.CafeServicePaladinName, AkkaConfig.CafeServiceSoldierName)
      case Comments => (AkkaConfig.CafeCommentsPaladinName, AkkaConfig.CafeCommentsSoldierName)
      case Images => (AkkaConfig.CafeImagesPaladinName, AkkaConfig.CafeImagesSoldierName)
      case _ => ("", "")
    }
  }

  private def sendTask(crawlPreData: Map[String, String]): Unit = {
    // How to get the Akka actor by target actor'name
    // https://stackoverflow.com/questions/25966635/how-to-get-akka-actor-by-name-as-an-actorref

    implicit val timeout = Timeout(5.seconds)
    val king = AkkaConfig.CafeKingName
    // Send the crawler pre-data to each Paladins.
//    val allPart = List(Basic, Services, Comments, Images)
    val allPart = List(Basic)
    for (part <- allPart) {
      val (paladin, soldier) = this.getActorSelection(part)
      val soldierID = this.SoldierID
      context.system.actorSelection(s"user/$king/$paladin/$soldier-$soldierID").resolveOne().onComplete{
        case Success(actorRef) =>
          // Ensure that crawl soldier has done previous task.
          val answer = actorRef ? AreYouDonePreviousTask
          val checksum = this.check.waitAnswer(answer, actorRef.path.toString)
          if (checksum.toString.equals("Yes")) {
            val data = if (this.UnderWaitDataList.isEmpty.equals(false)) {
              this.UnderWaitDataList.toList.apply(1)
            } else {
              crawlPreData
            }
            actorRef ! CrawlTask("Here is the crawl pre-data.", data)
          } else {
            // Save data to listbuffer to wait for previous task has done
            UnderWaitDataList += crawlPreData
            // Keep working after save data
          }
        case Failure(ex) =>
          if (WorkStatus.Working.equals(false)) {
            log.error(s"The AKKA actor path 'user/$king/$paladin/$soldier-$soldierID' doesn't exist! Please check it again.")
            //        case Failure(ex) => log.error(s"The AKKA actor 'user/$king/$paladin/$soldier-$soldierID' still working! Please wait.")
          }
      }
    }
  }


  override def receive: Receive = {

    case SearchPreData(content, soldierID) =>
      log.info("Roger that! Start to sniff all data of target topic og Kafka server.")
      this.SoldierID = soldierID

      implicit val groupID = "crawler-soldier"
      val cm = new DataConsumerManagement(this.check.getActorIndex(self)) {
        override def getMsg(timeoutMins: Int)(implicit consumer: KafkaConsumer[String, String]): Unit = {
          while (true) {
            val records = consumer.poll(timeoutMins).asScala
            for (record <- records) {
              if (record.value() != "" && record.value() != " ") {
                val crawlPreData = parseData(record.value())
                sendTask(crawlPreData)
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
