FROM busybox:1.36

ENV RUN_SECONDS=60
ENV CPU_WORKERS=4

COPY cpu_burn_parallel.sh /cpu_burn_parallel.sh
RUN chmod +x /cpu_burn_parallel.sh

CMD ["/cpu_burn_parallel.sh"]
