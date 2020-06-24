package Cafe_GoogleMap_Crawler

import scala.sys.process._


class TasksExecutor {

  val Path = "src/main/scala/Cafe_GoogleMap_Crawler/crawler_running_code"

  def runCode(preData: Map[String, String]): Unit = {
    // 1. Get the data which be saved in the collection
    val crawlPart = Basic
    val id = preData.get("id")
    val api = preData.get("url")
    val lat = preData.get("lat")
    val lng = preData.get("lng")

    // 2. Assign the value which we got to the string type value as a command line
    val runningCmd = s"python $Path/googlemap_cafe_with_akka.py " +
      s"--crawl-part $crawlPart --cafe-googlemap-api $api --cafe-id $id --cafe-lat $lat --cafe-lng $lng --sleep enable"
    println("[INFO] Running Python Code Command Line: \n" + runningCmd)
    val runningResult = runningCmd.!!
    println(s"[DEBUG] running command line result: $runningResult")
  }

}

