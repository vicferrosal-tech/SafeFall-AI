/*M!999999\- enable the sandbox mode */ 
-- MariaDB dump 10.19-11.8.3-MariaDB, for debian-linux-gnu (aarch64)
--
-- Host: localhost    Database: personas
-- ------------------------------------------------------
-- Server version	11.8.3-MariaDB-0+deb13u1 from Debian

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*M!100616 SET @OLD_NOTE_VERBOSITY=@@NOTE_VERBOSITY, NOTE_VERBOSITY=0 */;

--
-- Table structure for table `caidas`
--

DROP TABLE IF EXISTS `caidas`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `caidas` (
  `fecha` datetime DEFAULT NULL,
  `ip` varchar(50) DEFAULT NULL,
  `ruta_imatge` varchar(100) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_uca1400_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `caidas`
--

LOCK TABLES `caidas` WRITE;
/*!40000 ALTER TABLE `caidas` DISABLE KEYS */;
set autocommit=0;
INSERT INTO `caidas` VALUES
(NULL,'1.1.1.1','/prova'),
('2026-04-08 00:00:00','10.115.45.216','20260408_125258.jpg'),
('2026-04-08 00:00:00','10.115.45.216','20260408_125303.jpg'),
('2026-04-08 00:00:00','10.115.45.216','20260408_125308.jpg'),
('2026-04-08 00:00:00','10.115.45.216','20260408_125313.jpg'),
('2026-04-08 00:00:00','10.115.45.216','20260408_125318.jpg'),
('2026-04-08 00:00:00','10.115.45.216','20260408_125428.jpg'),
('2026-04-08 00:00:00','10.115.45.216','20260408_125433.jpg'),
('2026-04-08 00:00:00','10.115.45.216','20260408_125438.jpg'),
('2026-04-08 00:00:00','10.115.45.216','20260408_125443.jpg'),
('2026-04-08 00:00:00','10.115.45.216','20260408_125448.jpg'),
('2026-04-08 00:00:00','10.115.45.216','20260408_125453.jpg'),
('2026-04-08 00:00:00','10.115.45.216','20260408_130454.jpg'),
('2026-04-08 00:00:00','10.115.45.216','20260408_130949.jpg'),
('2026-04-08 00:00:00','10.115.45.216','20260408_131401.jpg'),
('2026-04-08 00:00:00','10.115.45.216','20260408_131406.jpg'),
('2026-04-08 00:00:00','10.115.45.216','20260408_131411.jpg'),
('2026-04-08 00:00:00','10.115.45.216','20260408_131417.jpg'),
('2026-04-08 00:00:00','10.115.45.216','20260408_131422.jpg'),
('2026-04-08 00:00:00','10.115.45.216','20260408_132321.jpg'),
('2026-04-08 00:00:00','10.115.45.216','20260408_133837.jpg'),
('2026-04-08 00:00:00','10.115.45.216','20260408_134002.jpg'),
('2026-04-20 00:00:00','1.1.1.1','prova2'),
('2026-04-20 00:00:00','1.1.1.1','prova3'),
('2026-04-20 00:00:00','1.1.1.1','prova4'),
('2026-04-20 00:00:00','1.1.1.1','prova5'),
('2026-04-20 00:00:00','1.1.1.1','prova6'),
('2026-04-22 00:00:00','1.1.1.1','prova6'),
('2026-04-22 00:00:00','1.1.1.1','prova3'),
('2026-04-22 00:00:00','1.1.1.1','prova4'),
('2026-04-22 00:00:00','1.1.1.1','prova5'),
('2026-04-22 00:00:00','1.1.1.1','prova7'),
('2026-04-22 00:00:00','1.1.1.1','prova7'),
('2026-04-22 00:00:00','1.1.1.1','prova7'),
('2026-04-22 00:12:00','1.1.1.1','prova7'),
('2026-04-22 13:12:00','1.1.1.1','prova7');
/*!40000 ALTER TABLE `caidas` ENABLE KEYS */;
UNLOCK TABLES;
commit;

--
-- Table structure for table `cameres`
--

DROP TABLE IF EXISTS `cameres`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `cameres` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `camera` varchar(50) DEFAULT NULL,
  `ip` varchar(50) DEFAULT NULL,
  `persones` int(11) DEFAULT NULL,
  `ultim_heartbeat` datetime DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_uca1400_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `cameres`
--

LOCK TABLES `cameres` WRITE;
/*!40000 ALTER TABLE `cameres` DISABLE KEYS */;
set autocommit=0;
INSERT INTO `cameres` VALUES
(1,'cam_10_138_91_216','10.138.91.216',1,NULL),
(2,'cam_10_115_45_216','10.115.45.216',3,'2026-04-30 13:04:47');
/*!40000 ALTER TABLE `cameres` ENABLE KEYS */;
UNLOCK TABLES;
commit;

--
-- Table structure for table `detecions`
--

DROP TABLE IF EXISTS `detecions`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `detecions` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `date` datetime NOT NULL,
  `num_personas` int(11) NOT NULL,
  `ruta_imatge` varchar(255) DEFAULT NULL,
  `ubicacion` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=1562 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_uca1400_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `detecions`
--

LOCK TABLES `detecions` WRITE;
/*!40000 ALTER TABLE `detecions` DISABLE KEYS */;
set autocommit=0;
/*!40000 ALTER TABLE `detecions` ENABLE KEYS */;
UNLOCK TABLES;
commit;

--
-- Table structure for table `estat_camera`
--

DROP TABLE IF EXISTS `estat_camera`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `estat_camera` (
  `ip` varchar(50) NOT NULL,
  `tumbat` tinyint(1) NOT NULL DEFAULT 0,
  `hora` datetime NOT NULL,
  `alerta_enviada` tinyint(1) DEFAULT 0,
  PRIMARY KEY (`ip`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_uca1400_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `estat_camera`
--

LOCK TABLES `estat_camera` WRITE;
/*!40000 ALTER TABLE `estat_camera` DISABLE KEYS */;
set autocommit=0;
INSERT INTO `estat_camera` VALUES
('10.115.45.216',0,'2026-04-08 13:40:16',0),
('10.138.91.216',0,'2026-01-21 14:20:22',0);
/*!40000 ALTER TABLE `estat_camera` ENABLE KEYS */;
UNLOCK TABLES;
commit;

--
-- Table structure for table `rols`
--

DROP TABLE IF EXISTS `rols`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `rols` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `nom` varchar(20) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `nom` (`nom`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_uca1400_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `rols`
--

LOCK TABLES `rols` WRITE;
/*!40000 ALTER TABLE `rols` DISABLE KEYS */;
set autocommit=0;
/*!40000 ALTER TABLE `rols` ENABLE KEYS */;
UNLOCK TABLES;
commit;

--
-- Table structure for table `users`
--

DROP TABLE IF EXISTS `users`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `users` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `username` varchar(80) NOT NULL,
  `password_hash` varchar(128) NOT NULL,
  `rol` varchar(20) NOT NULL DEFAULT 'usuari',
  PRIMARY KEY (`id`),
  UNIQUE KEY `username` (`username`)
) ENGINE=InnoDB AUTO_INCREMENT=7 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_uca1400_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `users`
--

LOCK TABLES `users` WRITE;
/*!40000 ALTER TABLE `users` DISABLE KEYS */;
set autocommit=0;
INSERT INTO `users` VALUES
(2,'isaac','$2b$12$uJoep7QKXo9C2vt4Mo9Suu8Nq8cx4LMYNErtUZLsgOo9FCBdFaLle','usuari'),
(3,'victoria','$2b$12$cfCJSSmPcOF4GbX88tUr2.fi4ehbkPnez6A5MJWo8MN3NzxAI5coO','usuari'),
(4,'admin','$2b$12$1LubnTxD6FoyUU/PJXhh1uv9ugYDDd8aF4imr1CVbG.BZ3ECB.0wq','usuari'),
(6,'safefall','$2b$12$NDq8KqJ2UsLEHNp49M0oteXjOaxRq8gaZ9oLPQqkIIJM2aH.b.Biq','admin');
/*!40000 ALTER TABLE `users` ENABLE KEYS */;
UNLOCK TABLES;
commit;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*M!100616 SET NOTE_VERBOSITY=@OLD_NOTE_VERBOSITY */;

-- Dump completed on 2026-05-07 13:08:10
