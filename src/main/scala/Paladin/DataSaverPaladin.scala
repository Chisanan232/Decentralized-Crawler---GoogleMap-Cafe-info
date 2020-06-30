package Cafe_GoogleMap_Crawler.src.main.scala.Paladin

import Cafe_GoogleMap_Crawler.src.main.scala.{Basic, Services, Comments, Images}
import Cafe_GoogleMap_Crawler.src.main.scala.config._

import org.json4s.jackson.JsonMethods._
import org.json4s.DefaultFormats

import akka.actor.{Actor, ActorLogging}

import org.apache.spark.{SparkConf, SparkContext}
import com.datastax.spark.connector._


class DataSaverPaladin extends Actor with ActorLogging {

  val conf = new SparkConf(true)
    .set("spark.cassandra.connection.host", CassandraConfig.CassandraHost)
    .setMaster(CassandraConfig.CassandraMaster)
    .setAppName(CassandraConfig.CassandraAppName)
  val sc = new SparkContext(conf)

  private def parseData(data: String): Map[String, Any] = {
    implicit val dataFormatter = DefaultFormats
    parse(data).extract[Map[String, Any]]
  }


  private def writeData(keyspace: String, table: String, data: Map[String, Any]): Unit = {
    val sparkRDDData = this.sc.parallelize(data.values.toList.toSeq)
    val columns = table match {
      case "Basic" => SomeColumns("isClosed", "title", "address", "phone", "url", "businessHours", "rating", "googlemap", "id", "createdAt")
      case "Services" => SomeColumns("services", "googlemap", "id", "createdAt")
      case "Comments" => SomeColumns("comments", "googlemap", "id", "createdAt")
      case "Images" => SomeColumns("photos", "googlemap", "id", "createdAt")
      case _ => SomeColumns("key", "value")
    }
    sparkRDDData.saveToCassandra(keyspace, table, columns)
  }


  override def receive: Receive = {

    case CallDataSaverPaladin =>
      log.info("Got it!")


    case RunningTaskResult(content, part, data) =>
      log.info("Receive the crawl-result data!")

      val mapData = this.parseData(data)
      this.writeData("target_keyspace", part.toString, mapData)

  }

}
