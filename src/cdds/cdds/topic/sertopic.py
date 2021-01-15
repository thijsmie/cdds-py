from cdds.internal.dds import DDS
from cdds.internal.cfunc import c_call, c_callable


class SerTopic(DDS):


    @c_call("dds_sertopic_init")
    def sertopic_init()