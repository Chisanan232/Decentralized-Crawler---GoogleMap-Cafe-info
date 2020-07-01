package Cafe_GoogleMap_Crawler.src.main.scala

import Cafe_GoogleMap_Crawler.src.main.scala.config.CassandraConfig

import com.datastax.driver.core.Cluster

import scala.collection.mutable.ListBuffer
import scala.util.matching.Regex


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
      else if (index.equals(tables.length - 1)) {newTablesInfo += ele.toString.filterNot(";]".toSet)}
      else {newTablesInfo += ele}
    }

    newTablesInfo.toList
  }


  def getTablesName(keyspace: String): List[String] = {
    val tablesInfo = this.cluster.getMetadata().getKeyspace(keyspace).getTables()

    val format = Regex.quote(keyspace) + "\\.\\w{1,256} \\(" r
    val tablesName = format.findAllIn(tablesInfo.toString)

    val tablesNameList = new ListBuffer[String]()
    tablesName.foreach(ele => {
       tablesNameList += ele.split("\\.").apply(1).split(" \\(")apply(0)
    })

    tablesNameList.toList
  }


  def createTable(keyspace: String, name: String, part: CrawlPart): Unit = {
    val session = this.cluster.connect(keyspace)

    val SQLCmd = s"CREATE TABLE $name (" +
      s"column1 int , " +
      s"column2 int" +
      s") ;"

    val columns = part.toString match {
      case "Basic" => "\"isClosed\", title, address, phone, url, \"businessHours\", rating, googlemap, id, \"createdAt\""
      case "Services" => "services, googlemap, id, \"createdAt\""
      case "Comments" => "comments, googlemap, id, \"createdAt\""
      case "Images" => "photos, googlemap, id, \"createdAt\""
    }

    session.execute(SQLCmd)
  }


  def deleteTable(keyspace: String, name: String): Unit = {
    val session = this.cluster.connect(keyspace)

    val SQLCmd = s"DROP TABLE $name ;"

    session.execute(SQLCmd)
  }


  def closeSession(): Unit = {
    this.cluster.close()
  }

}
