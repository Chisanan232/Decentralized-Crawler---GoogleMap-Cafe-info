package Cafe_GoogleMap_Crawler

import scala.concurrent.{Await, Future}
import scala.concurrent.duration._

import akka.actor.{Actor, ActorLogging, ActorRef, ActorSelection, ActorSystem, Props}
import akka.util.Timeout
import akka.pattern.ask


class CafeKing extends Actor with ActorLogging{

  val check = new CheckMechanism

  var CafeNum: Int = 0
  var CafeIDs: List[Any] = List[Any]()
  var APIs: List[Any] = List[Any]()
  var CafeLatss: List[Any] = List[Any]()
  var CafeLngs: List[Any] = List[Any]()
  var CafePreData: List[Any] = List[Any]()

  private final def getActorRef(actorName: String): ActorRef = {
    actorName match {
      case AkkaConfig.CafeBasicPaladinName => context.actorOf(Props[CafeBasicInfo], AkkaConfig.CafeBasicPaladinName)
      case AkkaConfig.CafeServicePaladinName => context.actorOf(Props[CafeService], AkkaConfig.CafeServicePaladinName)
      case AkkaConfig.CafeCommentsPaladinName => context.actorOf(Props[CafeComments], AkkaConfig.CafeCommentsPaladinName)
      case AkkaConfig.CafeImagesPaladinName => context.actorOf(Props[CafeImgs], AkkaConfig.CafeImagesPaladinName)
    }
  }

  private final def sendCallMsg(actor: ActorSelection, actorName: String)(implicit timeout: Timeout): Future[Any] = {
    actorName match {
      case AkkaConfig.CafeBasicPaladinName => actor ? CallCafeBasicPaladin
      case AkkaConfig.CafeServicePaladinName => actor ? CallCafeServicesPaladin
      case AkkaConfig.CafeCommentsPaladinName => actor ? CallCafeCommentsPaladin
      case AkkaConfig.CafeImagesPaladinName => actor ? CallCafeImagesPaladin
    }
  }

  private final def sendTaskMsg(actor: ActorSelection, actorName: String): Unit = {
    actorName match {
      case AkkaConfig.CafeBasicPaladinName => actor ! CrawlCafeBasic
      case AkkaConfig.CafeServicePaladinName => actor ! CrawlCafeServices
      case AkkaConfig.CafeCommentsPaladinName => actor ! CrawlCafeComments
      case AkkaConfig.CafeImagesPaladinName => actor ! CrawlCafeImages
    }
  }

  private final def runTask(actorName: String): Unit = {
    implicit val timeout = Timeout(10.seconds)
    val PaladinRef = this.getActorRef(actorName)
    val Paladin = context.actorSelection(PaladinRef.path)
    val Resp = this.sendCallMsg(Paladin, actorName)
    val Checksum = this.check.waitAnswer(Resp, PaladinRef.path.toString)
    if (Checksum.equals(true)) this.sendTaskMsg(Paladin, actorName)
  }


  override def preStart(): Unit = {
    log.info("Initial pre-data we need.")

    // Load data into King Actor.
    val ds = new DataSource
    val cafeDataNum = ds.dataNumber()
//    val cafeIDs = ds.GoogleMapCafeID()
//    val cafeGMAPIs = ds.GoogleMapAPI()
//    val cafeLats = ds.GoogleMapCafeLat()
//    val cafeLngs = ds.GoogleMapCafeLng()
    val preDataList = ds.GoogleMapCafeInfo()
    ds.closeSpark()

    this.CafeNum = cafeDataNum.toInt
//    this.CafeIDs = cafeIDs
//    this.APIs = cafeGMAPIs
//    this.CafeLatss = cafeLats
//    this.CafeLngs = cafeLngs
    this.CafePreData = preDataList.take(2)

    super.preStart()
  }


  override def receive: Receive = {

    case CrawlTarget(content, part) =>
      log.info("Start to crawl GoogleMap cafe data.")

      // We should classify the tasks into 4 parts: Basic info, Services, Comments and Images.
      // So we need to have 4 Paladins who has the responsibility of these tasks.
      log.info("Hello, every Paladin, I need your help.")

      this.runTask(AkkaConfig.CafeBasicPaladinName)
      this.runTask(AkkaConfig.CafeServicePaladinName)
      this.runTask(AkkaConfig.CafeCommentsPaladinName)
      this.runTask(AkkaConfig.CafeImagesPaladinName)

      // Active search Soldiers to sniff Kafka server message and forward them to crawler Soldiers
      val searchSoldiers = new Array[ActorRef](KafkaConfig.GoogleMapCrawlPreDataTopicPartitionsNum)
      for (soldierID <- 0.until(KafkaConfig.GoogleMapCrawlPreDataTopicPartitionsNum)) searchSoldiers(soldierID) = context.actorOf(Props[SearchSoldier], AkkaConfig.SearchPreDataSoldierName + s"-$soldierID")
      searchSoldiers.foreach(soldierRef => {
        val soldier = context.actorSelection(soldierRef.path)
        soldier ! SearchPreData("Please sniff data and here is your soldier ID.", soldierRef.path.name.takeRight(1).toInt)
      })

      // Import cafe info which crawler needs to use.
      val disPaladinRef = context.actorOf(Props[ProducePreDataPaladin], AkkaConfig.CafeDistributePaladinName)
      val distributePaladin = context.actorSelection(disPaladinRef.path)
      distributePaladin ! DistributePreData("Here are the all pre-data which be needed for cafe crawlers.", this.CafeNum, this.CafePreData)

  }

}
