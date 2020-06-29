package Cafe_GoogleMap_Crawler

import java.util
import java.util.Properties

import org.apache.kafka.clients.consumer.KafkaConsumer
import org.apache.kafka.common.TopicPartition


protected class DataConsumerManagement(implicit groupID: String) extends KafkaManagement {

  private val props = new Properties()
  //  val consumer = new KafkaConsumer[String, String](this.defineProperties())

  def defineProperties(): Properties = {
    /*
    If developer want to add more configuration or other setting, could overwrite this method.
     */
    this.props.put("bootstrap.servers", "localhost:9092")
    this.props.put("key.deserializer", "org.apache.kafka.common.serialization.StringDeserializer")
    this.props.put("value.deserializer", "org.apache.kafka.common.serialization.StringDeserializer")
    this.props.put("auto.offset.reset", "latest")
    this.props.put("group.id", groupID)
    props
  }


  def subscribeTopic(topic: String) (implicit consumer: KafkaConsumer[String, String]): Unit = {
    consumer.subscribe(util.Arrays.asList(topic))
  }


  def scanOnePartitionMsg(topic: String, partition: Int) (implicit consumer: KafkaConsumer[String, String]): Unit = {
    /***
     * Get all message of target topic with specific partition.
     * https://stackoverflow.com/questions/60560311/read-messages-from-kafka-topic-between-a-range-of-offsets
     */

    val tp = new TopicPartition(topic, partition)
    consumer.assign(util.Arrays.asList(tp))
    consumer.seekToBeginning(util.Arrays.asList(tp))
  }


  def scanAllPartitionsMsg(topic: String) (implicit consumer: KafkaConsumer[String, String]): Unit = {
    import scala.collection.JavaConverters.asJavaCollection

    // 1. Get all topic partitions
    val pm = new DataProducerManagement
    val partitionNum = pm.topicsList().length
    val topicPartitions = new Array[TopicPartition](partitionNum)
    for (partitionID <- 0.until(partitionNum)) topicPartitions(partitionID) = new TopicPartition(topic, partitionID)

    // 2. Subscribe target topic with partition
    // How to turn Scala List or Array, etc collection to Java util.collection?
    // https://stackoverflow.com/questions/8821461/scala-arraystring-to-java-collectionstring
    consumer.assign(asJavaCollection(topicPartitions))
    consumer.seekToBeginning(asJavaCollection(topicPartitions))
  }


  def getMsg(timeoutMins: Int) (implicit consumer: KafkaConsumer[String, String]): Unit = {
    /*
    This method should be overwrite in each actor.
     */

    println("******************************************")
    println("*                                        *")
    println("*    You should overwrite this method.   *")
    println("*                                        *")
    println("******************************************")

    // Here is some sample code you could use.
    //    while (true) {
    //      val records = consumer.poll(timeoutMins).asScala
    //      for (record <- records.iterator) {
    //        println(record.value())
    //      }
    //    }
  }


  def closeSession() (implicit consumer: KafkaConsumer[String, String]): Unit = {
    consumer.close()
  }

}
