'''
NumHopsTest.py
Author: Eric Ham
Description: Does analysis of num hops between client and guard for vanilla tor and counter raptor. 
Here, number of hops is defined as the number of ASes in a path from client to guard minus 1. It therefore
captures the connections between ASes, not the ASes themselves. 
'''

import numpy as np
import math
import matplotlib.pyplot as plt
import pylab

from pfi import *
import json
pfi = PFI("./libspookyhash.dylib", "./20180601_paths.txt", "./20180601_index.bin")
pfi.load()
print(pfi.verify())

#Vanilla Tor

#1: Find bandwidths for all guards

#ip_file = open('routeviews-rv2-20180729-1200.txt', 'r')
as_to_ip = open('as_guard.txt', 'r')

## create array for ip to AS. 
ip_to_as = {}
for line in as_to_ip:
	if line[0] == 'B':
		continue
	args = line.split('|')
	ip = args[1].strip()
	asn = args[0].strip()
	ip_to_as[ip] = asn


bw_file = open('guard_ips_with_bandwidth.txt', 'r')
ip_to_bw = {}
#make array of form: ip1: bw1, ip2: bw2...
for line in bw_file:
	args = line.split(' ')
	ip = args[0].strip(':')
	ip = ip.strip()
	ip_to_bw[ip] = int(args[1].strip())


#find AS with max bw. 
max_bw = 0
for ip in ip_to_bw:
	if ip_to_bw[ip] > max_bw:
		max_bw = ip_to_bw[ip]
		max_bw_as = ip_to_as[ip]


#Find num hops from all client ASes to this AS. 
client_AS_file = open('top400client.txt', 'r')
hop_array = []
hops = 0
num_ases = 0
avg_hops_vanilla = 0
for line in client_AS_file:
	AS = str(line.strip())
	#print('path: ' + str(pfi.get_path(str(AS), str(max_bw_as))))
	x = str(pfi.get_path(AS, str(max_bw_as)))
	if x == "None":
		#print('(Vanilla) Path from ' + str(AS) + ' to ' + str(max_bw_as) + ' cannot be found')
		continue
	args_x = x.split(',')
	#print(str(len(args_x)))

	#print(str(args_x) + '\n')

	hops = len(args_x) - 1 
	hop_array.append(hops)
	avg_hops_vanilla += hops
	num_ases += 1
#Get avg number of hops
avg_hops_vanilla /= num_ases
AS_to_ip_to_weight_vanilla = {}
with open("CounterRaptorWeightsVanilla.json") as data_file:
	data = json.load(data_file)
	for key, values in data.items():
		AS_to_ip_to_weight_vanilla[key] = values


	#1: Normalize guard weights. 
	for key in AS_to_ip_to_weight_vanilla:
		weight_sum = 0
		#AS_to_weight_normalized[key] = {}
		for guard_ip in AS_to_ip_to_weight_vanilla[key]:
			#if guard_ip in ip_to_as:

			#AS_to_weight_normalized[key][ip_to_as[guard_ip]] = AS_to_ip_to_weight[key][guard_ip]
			#else:
			#	continue
			#weight_sum += AS_to_weight_normalized[key][ip_to_as[guard_ip]]
			weight_sum += AS_to_ip_to_weight_vanilla[key][guard_ip]

		for guard_ip in AS_to_ip_to_weight_vanilla[key]:
			AS_to_ip_to_weight_vanilla[key][guard_ip] /= weight_sum

	hop_array_vanilla = []
	num_clients_vanilla = 0
	avg_hops_vanilla = 0
	for client in AS_to_ip_to_weight_vanilla:
		#print('client: ' + str(client))
		expected_num_hops_vanilla = 0
		num_hops_vanilla = 0
		for guard in AS_to_ip_to_weight_vanilla[key]:
			#print('guard: ' + str(guard))
			#get AS here instead of before so aren't cancelling. 
			x_vanilla = str(pfi.get_path(str(client), str(ip_to_as[guard])))
			
			if x_vanilla == "None":
				#print('(Counter Raptor) Path from ' + str(client) + ' to ' + str(guard) + ' cannot be found')
				continue
			args_x_vanilla = x_vanilla.split(',')
			num_hops_vanilla = len(args_x_vanilla) - 1
			expected_num_hops_vanilla += (num_hops_vanilla*AS_to_ip_to_weight_vanilla[client][guard])
		hop_array_vanilla.append(expected_num_hops_vanilla)
		avg_hops_vanilla += expected_num_hops_vanilla
		#print(avg_hops_cr)
		num_clients_vanilla +=1

	#Find Avg Num Hops
	avg_hops_vanilla /= num_clients_vanilla



#Counter Raptor (need to convert ips to ASes)
AS_to_ip_to_weight = {}
with open("CounterRaptorWeights.json") as data_file:
	data = json.load(data_file)
	for key, values in data.items():
		AS_to_ip_to_weight[key] = values


	#1: Normalize guard weights. 
	for key in AS_to_ip_to_weight:
		weight_sum = 0
		#AS_to_weight_normalized[key] = {}
		for guard_ip in AS_to_ip_to_weight[key]:
			#if guard_ip in ip_to_as:

			#AS_to_weight_normalized[key][ip_to_as[guard_ip]] = AS_to_ip_to_weight[key][guard_ip]
			#else:
			#	continue
			#weight_sum += AS_to_weight_normalized[key][ip_to_as[guard_ip]]
			weight_sum += AS_to_ip_to_weight[key][guard_ip]

		for guard_ip in AS_to_ip_to_weight[key]:
			AS_to_ip_to_weight[key][guard_ip] /= weight_sum

	hops_array_CR = []
	num_clients = 0
	avg_hops_cr = 0
	for client in AS_to_ip_to_weight:
		#print('client: ' + str(client))
		expected_num_hops = 0
		num_hops_cr = 0
		for guard in AS_to_ip_to_weight[key]:
			#print('guard: ' + str(guard))
			#get AS here instead of before so aren't cancelling. 
			x_cr = str(pfi.get_path(str(client), str(ip_to_as[guard])))
			
			if x_cr == "None":
				#print('(Counter Raptor) Path from ' + str(client) + ' to ' + str(guard) + ' cannot be found')
				continue
			args_x_cr = x_cr.split(',')
			num_hops_cr = len(args_x_cr) - 1
			expected_num_hops += (num_hops_cr*AS_to_ip_to_weight[client][guard])
		hops_array_CR.append(expected_num_hops)
		avg_hops_cr += expected_num_hops
		#print(avg_hops_cr)
		num_clients +=1

	#Find Avg Num Hops
	avg_hops_cr /= num_clients

#Counter Raptor (need to convert ips to ASes)
AS_to_ip_to_weight_nobw = {}
with open("CounterRaptorWeightsNoBW.json") as data_file:
	data = json.load(data_file)
	for key, values in data.items():
		AS_to_ip_to_weight[key] = values


	#1: Normalize guard weights. 
	for key in AS_to_ip_to_weight:
		weight_sum = 0
		#AS_to_weight_normalized[key] = {}
		for guard_ip in AS_to_ip_to_weight[key]:
			#if guard_ip in ip_to_as:

			#AS_to_weight_normalized[key][ip_to_as[guard_ip]] = AS_to_ip_to_weight[key][guard_ip]
			#else:
			#	continue
			#weight_sum += AS_to_weight_normalized[key][ip_to_as[guard_ip]]
			weight_sum += AS_to_ip_to_weight[key][guard_ip]

		for guard_ip in AS_to_ip_to_weight[key]:
			AS_to_ip_to_weight[key][guard_ip] /= weight_sum

	hops_array_nobw = []
	num_clients = 0
	avg_hops_nobw = 0
	for client in AS_to_ip_to_weight:
		#print('client: ' + str(client))
		expected_num_hops = 0
		num_hops_nobw = 0
		for guard in AS_to_ip_to_weight[key]:
			#print('guard: ' + str(guard))
			#get AS here instead of before so aren't cancelling. 
			x_nobw = str(pfi.get_path(str(client), str(ip_to_as[guard])))
			
			if x_nobw == "None":
				#print('(Counter Raptor) Path from ' + str(client) + ' to ' + str(guard) + ' cannot be found')
				continue
			args_x_nobw = x_nobw.split(',')
			num_hops_nobw = len(args_x_nobw) - 1
			expected_num_hops += (num_hops_nobw*AS_to_ip_to_weight[client][guard])
		hops_array_nobw.append(expected_num_hops)
		avg_hops_nobw += expected_num_hops
		#print(avg_hops_cr)
		num_clients +=1

	#Find Avg Num Hops
	avg_hops_nobw /= num_clients




#Results:
#Output avgs across all clients for vanilla tor and c r. 
print('Avg Number of Hops for Vanilla Tor: ' + str(avg_hops_vanilla))
print('Avg Number of Hops for Counter Raptor: ' + str(avg_hops_cr))
print('Avg Number of Hops for CR No BW: ' + str(avg_hops_nobw))

#Graph CDF of num hops avg for each AS
pylab.figure(figsize=(10,7))
sorted_data_vanilla = np.sort(hop_array_vanilla)		
sorted_data_cr = np.sort(hops_array_CR)									#put data in numerical order
sorted_data_nobw = np.sort(hops_array_nobw)
yvals_vanilla=np.arange(len(sorted_data_vanilla))/float(len(sorted_data_vanilla)-1)					#percentage  (float to cast to float) -1 part makes it line up well.
yvals_cr =np.arange(len(sorted_data_cr))/float(len(sorted_data_cr)-1)					#percentage  (float to cast to float) -1 part makes it line up well.  
yvals_nobw = np.arrange(len(sorted_data_nobw))/float(len(sorted_data_nobw)-1)
pylab.plot(sorted_data_vanilla,yvals_vanilla,linewidth=2.0,linestyle='solid',label=r'Vanilla')
pylab.plot(sorted_data_cr,yvals_cr,linewidth=2.0,linestyle='solid',label=r'CR')
pylab.plot(sorted_data_nobw,yvals_nobw,linewidth=2.0,linestyle='solid',label=r'CR')
pylab.title('Num Hops CDF')
pylab.legend(loc='upper left',fontsize=15)
pylab.title("CDF for Num Hops")
pylab.xlabel("Num Hops",fontsize=15)
pylab.ylabel("CDF",fontsize=15)
pylab.grid()
pylab.show()
