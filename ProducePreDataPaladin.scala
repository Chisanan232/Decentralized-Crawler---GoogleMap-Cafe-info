package Cafe_GoogleMap_Crawler

import akka.actor.{Actor, ActorLogging, ActorRef, Props}


class ProducePreDataPaladin extends Actor with ActorLogging {

  var allProduceTaskNum: Int = 0
  var currentProduceTaskDone = 0

  override def receive: Receive = {

    case DistributePreData(content, cafeDataNum, cafePreData) =>
      log.info("")
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
        val producerID = producerRef.path.name.takeRight(1).toInt
        producer ! ImportCafeCrawlerConditions("Here are the all pre-data which be needed for cafe crawlers.", DisCafePreData.toList.apply(producerID))
      })


    case ProduceFinish =>
      log.info("")
      this.currentProduceTaskDone += 1
      if (this.currentProduceTaskDone.equals(this.allProduceTaskNum)) {
        log.info("")
      }

  }

}
