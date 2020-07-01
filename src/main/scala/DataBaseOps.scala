package Cafe_GoogleMap_Crawler.src.main.scala

import Cafe_GoogleMap_Crawler.src.main.scala.config.CassandraConfig

import com.datastax.driver.core.Cluster


class DataBaseOps {

  // Create Cluster object
  // Should use withoutJMXReporting to avoid error ""
  // https://docs.datastax.com/en/developer/java-driver/3.5/manual/metrics/

  val cluster = Cluster.builder()
    .withoutJMXReporting()
    .addContactPoint(CassandraConfig.CassandraHost)
    .build()

}
