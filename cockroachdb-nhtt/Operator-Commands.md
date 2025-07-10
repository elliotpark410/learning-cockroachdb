**Required Ports:**
- Port 26257 used for inter-node and client-node communication
- Port 8080 used for Admin UI

**Network Configuration Best Practices**
- Symmetric routing:  Predictable latency, easier troubleshooting
- Low latency (<10ms): Faster consensus, better transaction throughput
- Sufficient bandwidth:	Faster replication, less downtime
- No NAT between nodes:	Reliable communication, secure node identity, consistent behavior

**Testing ping connectivity**

Create a list of hosts to test
```
cat > hosts.txt << EOF
node1
node2
node3
node4
node5
haproxy
EOF
```

```
for host in $(cat hosts.txt); do
  echo "Testing connectivity to $host..."
  ping -c 2 $host
done
```

**Verify SSH access to nodes**
```
for host in $(cat hosts.txt); do
  echo "Testing SSH connectivity to $host..."
  ssh -o StrictHostKeyChecking=no $host "hostname; exit"
done
```

**Measure Network Latency**
```
for host in $(cat hosts.txt); do
  echo "Measuring RTT to $host..."
  ping -c 5 $host | grep "avg"
done
```

**SSH into node 1**
```
ssh -o StrictHostKeyChecking=no root@node1
```

**Check vCPU resources**
```
lscpu | grep CPU
```

**Check memory resources**
```
free -h
```