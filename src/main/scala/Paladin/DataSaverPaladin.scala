package Cafe_GoogleMap_Crawler.src.main.scala.Paladin

import Cafe_GoogleMap_Crawler.src.main.scala.{Basic, Comments, CrawlPart, DataBaseOps, DataSource, Images, Services}
import Cafe_GoogleMap_Crawler.src.main.scala.config._
import org.json4s.jackson.JsonMethods._
import org.json4s.DefaultFormats
import akka.actor.{Actor, ActorLogging}
import org.apache.spark.{SparkConf, SparkContext}
import com.datastax.spark.connector._


class DataSaverPaladin extends Actor with ActorLogging {

  var TotalTaskNum: Int = 0
  var CurrentTaskNum: Map[String, Int] = Map[String, Int]()

  // Save data to database Cassandra has 2 methods
  // Method 1
  private val conf = new SparkConf(true)
    .set("spark.cassandra.connection.host", CassandraConfig.CassandraHost)
    .setMaster(CassandraConfig.CassandraMaster)
    .setAppName(CassandraConfig.CassandraAppName)
  private val sc = new SparkContext(conf)

  private def parseData(data: String): Map[String, Any] = {
    implicit val dataFormatter = DefaultFormats
    parse(data).extract[Map[String, Any]]
  }

  // Method 2
  private val ds = new DataSource
  private val dbo = new DataBaseOps

  private def writeData(keyspace: String, table: String, data: String): Unit = {
    // Method 1 to save data  to database Cassandra
    // Not finish
    // 1. Define a Seq type value
    // 2. Parse the target value to filter data we want
    // 3. Add into Seq type value
    // 4. parallelize by Spark method

    val sparkRDDData = this.sc.parallelize(data)
    val columns = table match {
      case "Basic" => SomeColumns("isClosed", "title", "address", "phone", "url", "businessHours", "rating", "googlemap", "id", "createdAt")
      case "Services" => SomeColumns("services", "googlemap", "id", "createdAt")
      case "Comments" => SomeColumns("comments", "googlemap", "id", "createdAt")
      case "Images" => SomeColumns("photos", "googlemap", "id", "createdAt")
      case _ => SomeColumns("key", "value")
    }
//    sparkRDDData.saveToCassandra(keyspace, table, columns)
  }


  private def saveData(keyspace: String, table: String, part: CrawlPart, data: String): Unit = {
    // Method 2 to save data  to database Cassandra

    if (this.dbo.getTablesName(keyspace).contains(table).equals(false)) this.dbo.createTable(keyspace, table, part)
    this.ds.saveDataToCassandra(keyspace, table, this.ds.convertJsonToDF(data))
  }


  override def receive: Receive = {

    case CallDataSaverPaladin(content, tasksNum) =>
      this.TotalTaskNum = tasksNum
      log.info("Got it! Will wait for data coming ...")


    case RunningTaskResult(content, part, data) =>
      log.info("Receive the crawl-result data!")

      val tableName = part.toString match {
        case "Basic" => "cafe_basic"
        case "Services" => "cafe_services"
        case "Comments" => "cafe_comments"
        case "Images" => "cafe_images"
        case _ => "none"
      }

      // Initial current task number
      if (this.CurrentTaskNum.keys.toList.contains(tableName).equals(false)) this.CurrentTaskNum += (tableName -> 0)

      AkkaConfig.CrawlSaverPattern.toString match {
        case "JsonFile" =>
          log.info("Will write data to file as Json type file.")
          val index = this.CurrentTaskNum(tableName)
          this.ds.saveDataToJsonFile(tableName, index, this.ds.convertJsonToDF(data))
          sender() ! SaveFinish("Here is the latest process about saving data.", this.CurrentTaskNum)
          // Update the index
          this.CurrentTaskNum += (tableName -> (index + 1))
        case "DataBase" =>
          log.info("Will write data to database -- Cassandra.")
          this.saveData(CassandraConfig.Keyspace, tableName, part, data)
          sender() ! SaveFinish("Here is the latest process about saving data.", this.CurrentTaskNum)
          // Update the index
          this.CurrentTaskNum += (tableName -> (this.CurrentTaskNum(tableName) + 1))
      }

  }

}
