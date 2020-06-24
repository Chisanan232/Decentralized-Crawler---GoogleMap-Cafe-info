name := "KobeDataScience"

version := "0.1"

scalaVersion := "2.12.11"

/*
 * Akka: https://doc.akka.io/docs/akka/2.3/intro/getting-started.html
 * Kafka: https://doc.akka.io/docs/alpakka-kafka/current/home.html#project-info
 */

libraryDependencies ++= {

  val SparkVersion = "2.4.5"
  val AkkaVersion = "2.5.31"
  val AkkaKafkaVersion = "2.0.3"
  val AkkaCassandraVersion = "2.0.0"
  val KafkaVersion = "2.5.0"
  val CassandraVersion = ""

  Seq(
    // Spark
    "org.apache.spark" %% "spark-core" % SparkVersion,
    "org.apache.spark" %% "spark-streaming" % SparkVersion,
    "org.apache.spark" %% "spark-sql" % SparkVersion,
    "org.apache.spark" %% "spark-streaming-kafka-0-10-assembly" % SparkVersion,
    // Akka
    "com.typesafe.akka" %% "akka-actor" % AkkaVersion,
    "com.typesafe.akka" %% "akka-remote" % AkkaVersion,
    "com.typesafe.akka" %% "akka-stream" % AkkaVersion,
    // Cassandra
    "com.lightbend.akka" %% "akka-stream-alpakka-cassandra" % AkkaCassandraVersion,
    "com.datastax.cassandra" % "cassandra-driver-core" % "4.0.0",
//    "com.datastax.cassandra" % "cassandra-driver-core" % "4.0.0" pomOnly(),
    // Kafka
    "com.typesafe.akka" %% "akka-stream-kafka" % AkkaKafkaVersion,
    "org.apache.kafka" %% "kafka" % KafkaVersion,
    "org.apache.kafka" % "kafka-clients" % KafkaVersion,
//    "org.apache.kafka" % "kafka-log4j-appender" % "0.9.0",
//  "org.apache.kafka" % "kafka-streams" % KafkaVersion,
//  "org.apache.kafka" % "kafka-clients" % KafkaVersion,
    // The package which targets to handle with og message.
//    "ch.qos.logback" % "logback-classic" % "1.1.3" % Runtime,
//    "org.slf4j" % "slf4j-api" % "1.7.5",
//    // Other packages
//    "com.typesafe" % "config" % "1.3.0",
    "log4j" % "log4j" % "1.2.16"
  )

}

resolvers ++= Seq(
  "Typesafe repository" at "http://repo.typesafe.com/typesafe/releases/"
)

//excludeDependencies ++= Seq(
////  "ch.qos.logback" % "logback-classic",
//  "org.slf4j" % "log4j-over-slf4j"
//)
