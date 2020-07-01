package Cafe_GoogleMap_Crawler.src.main.scala.Paladin

import Cafe_GoogleMap_Crawler.src.main.scala.{Basic, Services, Comments, Images}
import Cafe_GoogleMap_Crawler.src.main.scala.DataBaseOps
import Cafe_GoogleMap_Crawler.src.main.scala.config._

import org.json4s.jackson.JsonMethods._
import org.json4s.DefaultFormats

import akka.actor.{Actor, ActorLogging}

import org.apache.spark.{SparkConf, SparkContext}
import com.datastax.spark.connector._


class DataSaverPaladin extends Actor with ActorLogging {

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
  private val dbo = new DataBaseOps

  private def writeData(keyspace: String, table: String, data: String): Unit = {
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


  override def receive: Receive = {

    case CallDataSaverPaladin =>
      log.info("Got it!")


    case RunningTaskResult(content, part, data) =>
      log.info("Receive the crawl-result data!")

      val mapData = this.parseData(data)
      this.writeData("target_keyspace", part.toString, data)

  }

}
