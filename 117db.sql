-- phpMyAdmin SQL Dump
-- version 4.6.6
-- https://www.phpmyadmin.net/
--
-- Host: db
-- Generation Time: Feb 27, 2017 at 08:01 AM
-- Server version: 10.1.21-MariaDB-1~jessie
-- PHP Version: 7.0.15

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Database: `117db`
--

-- --------------------------------------------------------

--
-- Table structure for table `customer`
--

CREATE TABLE `customer` (
  `userid` int(11) NOT NULL,
  `geocode_la` double DEFAULT NULL,
  `geocode_lo` double DEFAULT NULL,
  `connection` tinyint(1) DEFAULT NULL,
  `time` double DEFAULT NULL,
  `status` tinytext
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

--
-- Dumping data for table `customer`
--

INSERT INTO `customer` (`userid`, `geocode_la`, `geocode_lo`, `connection`, `time`, `status`) VALUES
(2261287, 1, 1, 0, 0, 'b'),
(2261288, 0.909900381702131, 0.499504546234933, 1, 0, 'a'),
(2261289, 0.909900381702131, 0.499504546234933, 1, 0, 'a'),
(2261290, 0.909900381702131, 0.499504546234933, 1, 0, 'a'),
(2261291, 0.909900381702131, 0.499504546234933, 1, 0, 'a'),
(2261292, 0.909900381702131, 0.499504546234933, 1, 0, 'a'),
(2261293, 0.909900381702131, 0.499504546234933, 1, 0, 'a'),
(2261294, 0.909900381702131, 0.499504546234933, 1, 0, 'a');

--
-- Indexes for dumped tables
--

--
-- Indexes for table `customer`
--
ALTER TABLE `customer`
  ADD PRIMARY KEY (`userid`);

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
