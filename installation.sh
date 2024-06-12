#!/usr/bin/env bash

sudo apt-get install openjdk-8-jdk

sed -i '100i export JAVA_HOME=/usr/lib/jvm/java-8-openjdk-amd64/' .bashrc
sed -i '101i export PATH=$JAVA_HOME/bin:$PATH' .bashrc

java -version

wget https://archive.apache.org/dist/zookeeper/zookeeper-3.6.1/apache-zookeeper-3.6.1-bin.tar.gz

tar -zxf apche-zookeeper-3.6.1-bin.tar.gz
mv apche-zookeeper-3.6.1-bin zookeeper

cd zookeeper
mkdir data

cd conf

cp zoo_sample.cfg zoo.cfg

sed '12d' zoo.cfg
sed '12i dataDir=/home/cc/zookeeper/data' zoo.cfg

cd 

wget https://archive.apache.org/dist/storm/apache-storm-2.1.0/apache-storm-2.1.0.tar.gz

tar -zxf apache-storm-2.1.0.tar.gz
mv apache-storm-2.1.0 storm

cd storm
cd conf

cat <<EOL > storm.yaml
storm.zookeeper.servers:
    - "localhost"
storm.local.dir: "/home/cc/storm/data"
nimbus.thrift.port: 6667
ui.port: 8081
nimbus.seeds: ["localhost", "127.0.0.1"]
supervisor.slots.ports:
    - 6700
    - 6701
    - 6702
    - 6703
    - 6704
    - 6705

EOL






