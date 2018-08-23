# This is in MessageCenter -> worker object. This is called in ExpData -> sendCommand
def save(self,rf_data, gen_ts, sent_ts, recv_ts, addr):
        if self.fileALL:
            head = self.packHdr.pack(0x7e, gen_ts, sent_ts, recv_ts,
                    int(addr[0].split('.')[-1]),len(rf_data))
            self.writing = True
            self.fileALL.write(head+rf_data)
            self.writing = False
            
# process_rx in XBeeWifiNetwork triggers all the functions in XBeeMessageFuns to save received data
def process_rx(self, data, recv_ts) :
    try:
        addr = data[1]
        data_group = data[0]
        rf_data_group,sent_ts = PayloadPackage.unpack(data_group)
        for gen_ts,rf_data in rf_data_group :
            XBeeMessageFuncs.process_funcs[ord(rf_data[0])](self, rf_data,gen_ts, sent_ts, recv_ts, addr)
        self.updateStatistics(len(data_group))
    except:
        self.log.error(repr(data))
        self.log.error(traceback.format_exc())