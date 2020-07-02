package Cafe_GoogleMap_Crawler.src.main.scala

import java.nio.file.{Path, Paths, Files}

import org.apache.spark.{SparkContext, sql}
import org.apache.spark.sql.{DataFrame, SparkSession}
import org.apache.spark.sql.functions._


class FileOpts {

  val DataSaverPath = "src/main/scala/Cafe_GoogleMap_Crawler/crawl-data/"

  def ensureDirPathExist(dirPath: String): Unit = {
    val dir = Paths.get(this.DataSaverPath + dirPath)
    if (! Files.exists(dir)) Files.createDirectory(dir)
  }

}


/***
 * Original data operators
 */
class DataSource {

  val DataFilePath = "src/main/scala/Cafe_GoogleMap_Crawler/src/resources/googlemapList-main.json"

  val spark: SparkSession = SparkSession.builder()
    .appName("Cafe in GoogleMap decentralized crawler")
    .master("local[*]")
    .getOrCreate()

  // How to import spark.implicits?
  // https://stackoverflow.com/questions/39968707/spark-2-0-missing-spark-implicits
  import spark.implicits._

  private val fileIO = new FileOpts

  private def readData(): sql.DataFrame = {
//    spark.read.option("multiline", "true").json(this.DataFilePath)
//    this.spark.read.json(spark.sparkContext.wholeTextFiles(this.DataFilePath).values)
    this.spark.read.json(this.DataFilePath)
  }


  def dataNumber(): Float = {
    val data = this.readData()
    data.count()
  }


  def GoogleMapAPI(): List[Any] = {
    val data = this.readData()
    data.select("googlemap.url").rdd.map(_.toSeq.toList).collect().flatten.toList
  }


  def GoogleMapCafeLat(): List[Any] = {
    val data = this.readData()
    data.select("googlemap.lat").rdd.map(_.toSeq.toList).collect().flatten.toList
  }


  def GoogleMapCafeLng(): List[Any] = {
    val data = this.readData()
    data.select("googlemap.lng").rdd.map(_.toSeq.toList).collect().flatten.toList
  }


  def GoogleMapCafeID(): List[Any] = {
    val data = this.readData()
    data.select("id").rdd.map(_.toSeq.toList).collect().flatten.toList
  }


  def GoogleMapCafeInfo(): List[Any] = {
    val data = this.readData()

    // How to get dataframe with target multiple columns
    // https://stackoverflow.com/questions/34938770/upacking-a-list-to-select-multiple-columns-from-a-spark-data-frame/34938905#34938905

    // How to convert data to Map type data in Scala. (ex: ("id" -> "123", "url" -> "https://www.test.com"))
    // https://stackoverflow.com/questions/54797315/convert-multiple-columns-into-a-column-of-map-on-spark-dataframe-using-scala

    // What does syntax "_*" meaning in Scala
    // https://stackoverflow.com/questions/7938585/what-does-param-mean-in-scala

    val dfColumns = data.select("id": String, "googlemap.url": String, "googlemap.lat": String, "googlemap.lng": String)
    val dfColumnsData = dfColumns.columns.flatMap(c => Seq(lit(c), col(c)))
    //  println(t.withColumn("TestColumn", map(tt:_*)).show(false))
    val dfMapData = dfColumns.withColumn("crawlPreData", map(dfColumnsData:_*)).toDF()
    dfMapData.select("crawlPreData").rdd.map(_.toSeq.toList).collect().flatten.toList
  }


  def convertJsonToDF(data: String): DataFrame = {

    // How to convert Json type data to SQL DataFrame via Spark
    // https://stackoverflow.com/questions/38271611/how-to-convert-json-string-to-dataframe-on-spark
    // http://spark.apache.org/docs/2.2.0/sql-programming-guide.html#json-datasets

    Seq(data).toDF()
  }


  implicit def intToString(index: Int): String = index.toString

  def saveDataToJsonFile(table: String, index: String, data: DataFrame): Unit = {
    // 1. Check whether the target directory path exist or not
    val tableDir = this.fileIO.DataSaverPath + table
    this.fileIO.ensureDirPathExist(tableDir)
    val jsonFile = tableDir + s"/index_$index.json"
    Files.createFile(Paths.get(jsonFile))

    // 2. Save data into file in target directory
    data.write.json(jsonFile)
  }


  def saveDataToCassandra(keyspace: String, table: String, data: DataFrame): Unit = {

    // Save data to database Cassandra methods
    // https://stackoverflow.com/questions/41248269/inserting-data-into-cassandra-table-using-spark-dataframe

    data.write.format("org.apache.spark.sql.cassandra").options(Map("keyspace" -> keyspace, "table" -> table)).save()
  }


  def closeSpark(): Unit = {
    /*
    https://stackoverflow.com/questions/50504677/java-lang-interruptedexception-when-creating-sparksession-in-scala
     */
    this.spark.sparkContext.stop()
    this.spark.close()
  }

}


//object DataProcessTest extends App {
//
//  val dst = new DataSource
//  println("**********************************")
//
//  import scala.util.parsing.json.JSONObject
//  import org.json4s.jackson.JsonMethods._
//  import org.json4s.DefaultFormats
//
//  val tt = dst.Debug()
//  tt.foreach(ele => {
//    val testJson = JSONObject(ele.asInstanceOf[Map[String, String]])
//    println("**********************************")
//    println(testJson)
//    println(testJson.toString())
//    implicit val jsonformat = DefaultFormats
//    println(parse(testJson.toString()).extract[Map[String, Any]])
//  })
//
////  val data = dst.readData()
////  //    data.select("googlemap.url, googlemap.lat, googlemap.lng, id").rdd.map(_.toSeq.toList).collect().flatten.toList
////  //    val columns = Seq("googlemap.url", "googlemap.lat", "googlemap.lng", "id")
////  //    val t = data.select(columns.head, columns.tail:_*)
////  val t = data.select("id": String, "googlemap.url": String, "googlemap.lat": String, "googlemap.lng": String)
//////  println(t.show(10))
////  val tt = t.columns.flatMap(c => Seq(lit(c), col(c)))
//////  println(t.withColumn("TestColumn", map(tt:_*)).show(false))
//////  testYee.rdd.map(_.toSeq.toList).collect().flatten.toList
////  val testYee = t.withColumn("TestColumn", map(tt:_*)).toDF()
////  println(t.show(10))
////  println("**********************************")
////  println(testYee.show(10))
////  println("**********************************")
////  println(testYee.select("TestColumn").rdd.map(_.toSeq.toList).collect().flatten.toList)
////  println(testYee.select(col("TestColumn").getField("id")))
//////  println(testYee.select("TestColumn"))
////  println("**********************************")
////  println(testYee.select("TestColumn").toJSON)
////  println("**********************************")
//
//  dst.closeSpark()
//
//}
