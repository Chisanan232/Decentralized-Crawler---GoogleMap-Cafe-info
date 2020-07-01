package Cafe_GoogleMap_Crawler.src.main.scala

sealed trait SaverPattern

case object JsonFile extends SaverPattern
case object DataBase extends SaverPattern
