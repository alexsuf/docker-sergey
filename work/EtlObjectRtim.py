from EtlFlow import *



class EtlFlowRtim(EtlFlow):
    flow_name = 'rtim'
    def __init__(self, current_env='dev'):
        """
        :param flow_name: Имя потока
        :param current_env: имя окружения
        """
        super.__init__(current_env)

        self.flow_id = f"{self.project_name}_{self.flow_name}_{self.current_env}"

        sparkConfig = self.getSparkConfig()

        self.spark_session = SparkConnect(sparkConfig).create()

        #Список всех объектов потока
        self.etlObjectDict = self.__getEtlObjectDict()


    def table_init(self):
        self.customers = self.EtlObjectJDBC(object_name='customers')


    def calc_stg(self):
        print(self.customers.toPandas())



if __name__ == '__main__':
    etlFlowRtim = EtlFlowRtim(current_env='dev')
    etlFlowRtim.calc_stg()





