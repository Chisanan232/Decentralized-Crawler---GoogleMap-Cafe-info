package Cafe_GoogleMap_Crawler.src.main.scala

import Cafe_GoogleMap_Crawler.src.main.scala.config.CassandraConfig

import com.datastax.driver.core.Cluster

import scala.collection.mutable.ListBuffer


class DataBaseOps {

  // Create Cluster object
  // Should use withoutJMXReporting to avoid error ""
  // https://docs.datastax.com/en/developer/java-driver/3.5/manual/metrics/

  private val cluster = Cluster.builder()
    .withoutJMXReporting()
    .addContactPoint(CassandraConfig.CassandraHost)
    .build()

  def getTables(keyspace: String): List[String] = {
    val tablesInfo = this.cluster.getMetadata().getKeyspace(keyspace).getTables()
    val tables = tablesInfo.toString.split(";,")

    var newTablesInfo = new ListBuffer[String]()

    for((ele, index) <- tables.zipWithIndex) {
      if (index.equals(0)) {newTablesInfo += ele.toString.drop(1)}
      else if (index.equals(newTables.length - 1)) {newTablesInfo += ele.toString.filterNot(";]".toSet)}
      else {newTablesInfo += ele}
    }

    newTablesInfo.toList
  }

}
