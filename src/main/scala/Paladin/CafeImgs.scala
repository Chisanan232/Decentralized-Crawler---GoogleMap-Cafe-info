package Cafe_GoogleMap_Crawler.src.main.scala.Paladin

import Cafe_GoogleMap_Crawler.src.main.scala.config._

import akka.actor.{Actor, ActorLogging}


class CafeImgs extends Actor with ActorLogging {

  override def receive: Receive = {

    case CallCafeImagesPaladin =>
      log.info("I Receive task!")
      val consumerLeaderPath = context.self.path
      val msg = s"I'm ready! I'm $consumerLeaderPath"
      val parent = context.actorSelection(context.parent.path)
      //      println("*******===========**** Consumer ***===========*******===========")
      //      println(msg)
      //      println(context.parent.path)
      //      println(parent)
      //      println("*******===========*******===========*******===========")
      sender() ! msg

  }

}

