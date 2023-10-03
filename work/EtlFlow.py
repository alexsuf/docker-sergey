from dataclasses import dataclass
from pyspark.sql import SparkSession
from sqlalchemy import create_engine, text
import json
import pathlib
import pandas as pd

@dataclass
class EtlFlowConfig:
    project_name: str
    master_url: str
    master_schema: str

@dataclass
class SparkConfig:   
    flow_name: str 
    driver_memory: str = None
    executor_memory: str = None
    executor_instances: int = None
    spark_master: str = None #local/yarn/etc


@dataclass
class EtlObjectConfig:
    direction: str #source/target
    schema_name: str
    object_name: str
    driver_type: str #jdbc/file/etc
    db_type: str #postgres/oracle/etc
    host: str
    port: str
    database: str
    url: str
    user: str
    password: str


def getFlowConfig(env):
    # 
    curdir = pathlib.Path(__file__).parent.resolve()

    with open(f'{curdir}/../configs/flow_config_{env}.json', encoding='utf-8') as json_file:
        data = json.load(json_file)

    return EtlFlowConfig(**data)



class EtlFlow():
    def __init__(self, current_env='dev'):
        """
        :param flow_name: Имя потока
        :param current_env: имя окружения
        """
        flowConfig = getFlowConfig(current_env)
        self.project_name = flowConfig.project_name # 'cutsrv'
        self.master_schema = flowConfig.master_schema
        self.current_env = current_env
        self.flow_name = ""
        self.flow_id = ""
        self.etlObjectDict = {}
        self.masterConnect = MasterData(flowConfig.master_url).getConnection()
        

    def __execute_sql(self, sql, printSQL = 1):
        res = []
        if printSQL == 1:
            print(sql)
        result = self.masterConnect.execute(text(sql))
        for row in result:
            res.append(row)
        return res
    

    def __getEtlObjectDict(self):
        sql = f"""select schema_name, object_name, direction, driver_type, db_type, host, port, 
                database_name, user_name, user_pass
                from {self.master_schema}.dataobject
                where flow_id = '{self.flow_id}'
        """
        res = self.__execute_sql(sql)
        d = {}
        for t in res:
            d[t.object_name] = EtlObjectConfig(t.direction, t.schema_name, t.object_name, t.driver_type, 
                                               t.db_type, t.host, t.port, t.database_name, t.user_name, t.user_pass)

        return d
    

    
    def EtlObjectJDBC(self, object_name, where='1=1', chunk_size=1_000_000):
        """
        Создане датафрейма чтения из объекта
        :return: Подготовленный DataFrame
        """
        if object_name not in self.etlObjectDict:
            raise ValueError(f"Object '{object_name}' not found in dataobject table for '{self.flow_id}' flow")

        config = self.etlObjectDict[object_name]

        if config.driver_type != 'jdbc':
            raise ValueError(f"Object '{object_name}' has driver '{config.driver_type}', but jdbc needed")        
        
        conn = EtlObjectConnection(config)

        df = (self.spark_session.read.format('jdbc').
                option('driver', conn.driver).
                option('url', conn.driver).
                option('dbtable', f"{config.schema_name}.{config.object_name}").
                option('user', conn.user).
                option('password', conn.password).
                option('fetchsize', str(chunk_size))
                )
        return df.where(where)


    def getSparkConfig (self):
        sql = f"""select driver_memory, executor_memory, executor_instances, spark_master
                from {self.master_schema}.dataflow
                where flow_id = '{self.flow_id}'
        """
        df = self.__execute_sql(sql)[0]

        return SparkConfig(self.flow_id, df.driver_memory, df.executor_memory, df.executor_instances, df.spark_master)



class MasterData(object):
    __connect = None
    # инициализируем Singleton
    def __new__(cls, url):
        if not hasattr(cls, 'instance'):
            cls.instance = super(MasterData, cls).__new__(cls)
        return cls.instance

    def getConnection(self):
        if self.__connect == None:
            self.__connect = create_engine(self.url).connect()
        return self.__connect

    def __init__(self, url):
        self.url = url

    def __del__(self):
        self.__connect.close()


class SparkConnect():
    __spark_session = None

    def __init__(self, config):
        self.app_name = config.flow_id
        self.master=config.spark_master 
        self.driver_memory=config.driver_memory 
        self.executor_memory=config.executor_memory 
        self.executor_instances=config.executor_instances

    def create(self):
        """
        :param config: settings
        """
        if self.__spark_session == None:
            self.__spark_session = SparkSession.builder\
            .config("spark.driver.memory", self.driver_memory)\
            .config("spark.executor.memory", self.executor_memory)\
            .config("spark.executor.instances", self.executor_instances)\
            .master(self.master)\
            .appName(self.app_name)\
            .enableHiveSupport()\
            .getOrCreate()

        return self.__spark_session

    def __del__(self):
        self.__spark_session.stop()


class EtlObjectConnection():
    def __init__(self, config):
        """
        :param config: data-class of parameters
        """

        driver_dict = {'mssql': 'com.microsoft.sqlserver.jdbc.spark',
                'postgres': 'org.postgresql.Driver',
                'oracle': 'oracle.jdbc.driver.OracleDriver',
                'mysql': 'com.mysql.cj.jdbc.Driver',
                'clickhouse': 'com.clickhouse.jdbc.ClickHouseDriver',
                'sybase': 'net.sourceforge.jtds.jdbc.Driver'
                }

        def __url_ms(host, port, database):
            if len(host.split('\\')) > 1:
                # Если указан инстанс, то порт не указвыается
                port = None
            return f"jdbc:sqlserver://{host}{f':{port}' if port else ''}"\
                f"{f';databaseName={database}' if database else ''}"\
                f";encrypt=true;trustServerCertificate=true"
        
        def __url_pg(host, port, database):
            return f"jdbc:postgresql://{host}{f':{port}' if port else ''}{f'/{database}' if database else ''}"
        
        def __url_ora(host, port, database):
            return f"jdbc:oracle:thin:@://{host}{f':{port}' if port else ''}{f'/{database}' if database else ''}"
        
        url_dict = {'mssql': self.__url_ms,
                'postgres': self.__url_pg,
                'oracle': self.__url_ora,
                'mysql': "tbd",
                'clickhouse': "tbd",
                'sybase': "tbd"
                }

        self.driver_type = config.driver_type
        self.driver = driver_dict(config.db_type), 
        self.host = config.host
        self.port = config.port
        self.database = config.schema
        self.url = url_dict[config.driver](config.host, config.port, config.database)
        self.user = config.user
        self.password = config.password


