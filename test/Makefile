MAKE    := make -w
PWD     := $(shell pwd)
DATE    := $(shell date +'%Y_%m_%d_%H_%M_%S')

SERVER_ADDR     := 192.168.1.225
API_SERVER_ADDR := http://$(SERVER_ADDR)
SIP_SERVER_ADDR := $(SERVER_ADDR)
LOCAL_IP        := 192.168.1.223

LOGS_DIR     := $(PWD)/logs
SIPP_DIR     := $(PWD)/sipp

all:
	echo $(DATE)

api:
	@echo "\r\n"
	curl -D cookie -H "Content-type: application/json" -X POST -d '{"name": "admin", "password": "admin"}' $(API_SERVER_ADDR)/api/user/login
	curl -b cookie -H "Content-type: application/json" $(API_SERVER_ADDR)/api/extensions/status
	@echo "\r\n"

tcpdump:
	tcpdump -n -X dst host 192.168.1.157 or dst host 192.168.1.223 and "tcp[tcpflags] & (tcp-push) != 0"

sipp-test-ring:
	if [ ! -d $(LOGS_DIR) ];then mkdir $(LOGS_DIR);fi
	-sipp -sn uac $(SIP_SERVER_ADDR) -r 10 -i $(LOCAL_IP) -sf $(SIPP_DIR)/uac_ring.xml -inf $(SIPP_DIR)/data.csv -aa -trace_stat -stf $(LOGS_DIR)/sipp_$(DATE).csv -stat_delimiter ,

sipp-test-ring-bg:
	if [ ! -d $(LOGS_DIR) ];then mkdir $(LOGS_DIR);fi
	-nohup sipp -sn uac $(SIP_SERVER_ADDR) -r 10 -i $(LOCAL_IP) -sf $(SIPP_DIR)/uac_ring.xml -inf $(SIPP_DIR)/data.csv -aa -trace_stat -stf $(LOGS_DIR)/sipp_$(DATE).csv -stat_delimiter , -bg

sipp-test:
	if [ ! -d $(LOGS_DIR) ];then mkdir $(LOGS_DIR);fi
	-sipp -sn uac $(SIP_SERVER_ADDR) -r 5 -i $(LOCAL_IP) -sf $(SIPP_DIR)/uac.xml -inf $(SIPP_DIR)/data.csv -aa -trace_stat -stf $(LOGS_DIR)/sipp_$(DATE).csv -stat_delimiter ,

sipp-test-bg:
	if [ ! -d $(LOGS_DIR) ];then mkdir $(LOGS_DIR);fi
	-nohup sipp -sn uac $(SIP_SERVER_ADDR) -i $(LOCAL_IP) -sf $(SIPP_DIR)/uac.xml -inf $(SIPP_DIR)/data.csv -aa -trace_stat -stf $(LOGS_DIR)/sipp_$(DATE).csv -stat_delimiter , -bg


sipp-test-msg:
	if [ ! -d $(LOGS_DIR) ];then mkdir $(LOGS_DIR);fi
	-sipp -sn uac $(SIP_SERVER_ADDR) -i $(LOCAL_IP) -sf $(SIPP_DIR)/uac.xml -inf $(SIPP_DIR)/data.csv -aa -trace_stat -stf $(LOGS_DIR)/sipp_$(DATE).csv -stat_delimiter , -trace_msg -message_file $(LOGS_DIR)/sipp_$(DATE)_msg.txt

sipp-clean:
	rm -rf $(LOGS_DIR)/sipp_*.csv

api-test:
	$(PWD)/officelink_api_test.py install
	$(PWD)/officelink_api_test.py all $(SERVER_ADDR) noprint

clean:
