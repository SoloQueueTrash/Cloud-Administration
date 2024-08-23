# Decentralized Virtual CDN With Opportunistic Offloading

This project is focused on creating a decentralized Content Delivery Network (CDN) using Google Cloud, with an emphasis on GDPR compliance, data sovereignty, and privacy-first solutions. The goal is to design and implement a CDN service comparable to Cloudflare and Akamai, optimizing for performance, cost, architecture design, and predictive modeling.

## Project Goals
- **CDN Deployment:** Implement a CDN service using Google Cloud to handle global client requests.
- **Latency Reduction:** Deploy servers closer to users to minimize latency, balancing cost and performance.
- **Opportunistic Offloading:** Leverage client devices for caching, using up to 100MB per device, with constraints.
- **Reverse Proxy:** Deploy a reverse proxy to manage client-side caching and data sharing.

## Evaluation Criteria
- **Performance (5pts):** Measured by latency and throughput.
- **Cost (8pts):** Total cost of the solution, including VMs, storage, and traffic.
- **Architecture Design (5pts):** Quality of the overall architecture, including optimization and elasticity strategies.
- **Predictive Model (2pts):** Accuracy of the workload prediction model.

## Implementation Details
- **Load Balancer:** A small application server acting as a load balancer, returning CDN server IPs.
- **Cost Analysis:** Detailed cost breakdown included in the final report (max 2 pages).
- **Architecture Diagram:** Comprehensive explanation of the architecture and optimizations (max 5 pages).
- **ML Model:** Construct a machine learning model for workload prediction (max 2 pages).

## Tools and Technologies
- **Servers & Software:** NGINX, Memcache, MariaDB, Cassandra, Postgresql, MongoDB, Redis, Ceph.
- **Filesystems:** Ext4, ZFS, Btrfs.
- **Programming Languages:** Python, Java, Rust, C in NGINX.
- **Managed Services:** All Google Cloud Platform services.
- **Client Emulation:** Raspberry Pi-level devices (1 vCPU, 1GB RAM).
- **Admin Client:** Interface for asset management and dissemination across servers, using REST/HTTP with a self-signed certificate.

## Constraints
- **No JavaScript:** PHP, Node.js, or any other form of JavaScript is prohibited.
- **Security:** Use static IPs and self-signed certificates.

## Conclusion
This lab assignment is a competitive effort to develop a cost-effective, high-performance CDN with decentralized caching and workload prediction. The solution will be evaluated on various aspects, with a base grade of 10 points, and additional points awarded based on performance relative to other groups.

