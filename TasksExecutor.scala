package Cafe_GoogleMap_Crawler

import scala.util.matching.Regex
import scala.sys.process._


class TasksExecutor {

  val Path = "src/main/scala/Cafe_GoogleMap_Crawler/crawler_running_code"

  private def filterData(data: String): String = {
    val dataFormatter = "############################################################.{1,100000000}############################################################".r
    val targetData = dataFormatter.findFirstIn(data)
    if (targetData.isEmpty) {
      ""
    } else {
      targetData.get.toString
    }
  }


  def runCode(crawlPart: CrawlPart, preData: Map[String, String]): String = {
    // 1. Parse crawl pre-data. (Get the data which be saved in the collection)
    val id = preData.get("id").get.toString
    val api = preData.get("url").get.toString
    val lat = preData.get("lat").get.toString
    val lng = preData.get("lng").get.toString

    // 2. Assign the value which we got to the string type value as a command line
    val runningCmd = s"python $Path/googlemap_cafe_with_akka.py " +
      s"--crawl-part $crawlPart --cafe-googlemap-api $api --cafe-id $id --cafe-lat $lat --cafe-lng $lng --sleep enable"
    println("[INFO] Running Python Code Command Line: \n" + runningCmd)
    val runningResult = runningCmd.!!
    println(s"[DEBUG] running command line result: $runningResult")
    this.filterData(runningResult)
  }

}

