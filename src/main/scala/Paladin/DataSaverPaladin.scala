package Cafe_GoogleMap_Crawler.src.main.scala.Paladin

import Cafe_GoogleMap_Crawler.src.main.scala.config._

import akka.actor.{Actor, ActorLogging}

import org.apache.spark.{SparkConf, SparkContext}
import com.datastax.spark.connector._


class DataSaverPaladin extends Actor with ActorLogging {

  val conf = new SparkConf(true)
    .set("spark.cassandra.connection.host", CassandraConfig.CassandraHost)
    .setMaster(CassandraConfig.CassandraMaster)
    .setAppName(CassandraConfig.CassandraAppName)
  val sc = new SparkContext(conf)

  private def writeData(keyspace: String, table: String, data: String): Unit = {
    val sparkRDDData = this.sc.parallelize(data)
    val columns = table match {
      case "" => SomeColumns()
      case _ => SomeColumns("key", "value")
    }
    sparkRDDData.saveToCassandra(keyspace, table, columns)
  }


  override def receive: Receive = {

    case RunningTaskResult(content, data) =>
      log.info("Receive the crawl-result data!")

  }

}
