package Cafe_GoogleMap_Crawler.src.main.scala

import org.apache.spark.{SparkContext, sql}
import org.apache.spark.sql.SparkSession
import org.apache.spark.sql.functions._


/***
 * Original data operators
 */
class DataSource {

  val DataFilePath = "src/main/resources/googlemapList-main.json"

  val spark: SparkSession = SparkSession.builder()
    .appName("Cafe in GoogleMap decentralized crawler")
    .master("local[*]")
    .getOrCreate()

  // How to import spark.implicits?
  // https://stackoverflow.com/questions/39968707/spark-2-0-missing-spark-implicits
  import spark.implicits._

  private def readData(): sql.DataFrame = {
//    spark.read.option("multiline", "true").json(this.DataFilePath)
    this.spark.read.json(spark.sparkContext.wholeTextFiles(this.DataFilePath).values)
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
