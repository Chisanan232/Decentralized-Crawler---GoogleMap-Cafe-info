package Cafe_GoogleMap_Crawler.src.main.scala.Soldier

import Cafe_GoogleMap_Crawler.src.main.scala.CrawlPart

import scala.sys.process._


class TasksExecutor {

//  val Path = "src/main/scala/Cafe_GoogleMap_Crawler/crawler_running_code"
  val Path = "src/main/scala/Cafe_GoogleMap_Crawler/src/main/python"

  private def filterData(data: String): String = {
    val dataFormatter = "############################################################.{1,100000000}############################################################".r
    val targetData = dataFormatter.findFirstIn(data)
    if (targetData.isDefined) {
      targetData.get.toString.split("############################################################").toList.apply(1)
    } else {
      ""
    }
  }


  def runCode(crawlPart: CrawlPart, preData: Map[String, String]): String = {
    // 1. Parse crawl pre-data. (Get the data which be saved in the collection)
    val id = preData("id").toString
    val api = preData("url").toString
    val lat = preData("lat").toString
    val lng = preData("lng").toString

    // 2. Assign the value which we got to the string type value as a command line
    val runningCmd = s"python $Path/googlemap_cafe_with_akka.py " +
      s"--crawl-part $crawlPart --cafe-googlemap-api $api --cafe-id $id --cafe-lat $lat --cafe-lng $lng --sleep enable"
    println("[INFO] Running Python Code Command Line: \n" + runningCmd)
    val runningResult = runningCmd.!!
    println(s"[DEBUG] running command line result: $runningResult")
    this.filterData(runningResult)
  }

}

