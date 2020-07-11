package Cafe_GoogleMap_Crawler.src.main.scala.Paladin

import Cafe_GoogleMap_Crawler.src.main.scala.config._
import Cafe_GoogleMap_Crawler.src.main.scala.CheckMechanism
import Cafe_GoogleMap_Crawler.src.main.scala.Soldier.ProducePreDataSoldier

import akka.actor.{Actor, ActorLogging, ActorRef, Props}


class ProducePreDataPaladin extends Actor with ActorLogging {

  var allProduceTaskNum: Int = 0
  var currentProduceTaskDone: Int = 0

  private val check = new CheckMechanism

  override def receive: Receive = {

    case DistributePreData(content, cafeDataNum, cafePreData) =>
      log.info("Got it! Will start to produce pre-data of crawling ...")
      this.allProduceTaskNum = cafeDataNum

      // The pre-data should be a data type which like Json has Keyword-Value format.
//      val DisCafeIDs = cafeIDs.grouped(this.CafeNum / 10)
//      val DisCafeAPIs = cafeAPIs.grouped(this.CafeNum / 10)
//      val DisCafeLats = cafeLats.grouped(this.CafeNum / 10)
//      val DisCafeLngs = cafeLngs.grouped(this.CafeNum / 10)
      val DisCafePreData = cafePreData.grouped(cafeDataNum / KafkaConfig.GoogleMapCrawlPreDataTopicPartitionsNum)

      // Distribute these data to each Producer Soldiers
      val produceSoldiers = new Array[ActorRef](KafkaConfig.GoogleMapCrawlPreDataTopicPartitionsNum)
      for (producerID <- 0.until(KafkaConfig.GoogleMapCrawlPreDataTopicPartitionsNum)) produceSoldiers(producerID) = context.actorOf(Props[ProducePreDataSoldier], AkkaConfig.ProduceCafePreDataSoldierName + s"-$producerID")
      produceSoldiers.foreach(producerRef => {
        val producer = context.actorSelection(producerRef.path)
        producer ! ImportCafeCrawlerConditions("Here are the all pre-data which be needed for cafe crawlers.", DisCafePreData.toList.apply(this.check.getActorIndex(producerRef)))
      })


    case ProduceFinish =>
      log.info("Thank you for your help!")
      this.currentProduceTaskDone += 1
      if (this.currentProduceTaskDone.equals(this.allProduceTaskNum)) {
        log.info("Done to produce pre-data!")
        context.stop(self)
      }

  }

}
