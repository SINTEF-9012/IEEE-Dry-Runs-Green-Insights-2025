FROM busybox:1.36

ENV RUN_SECONDS=60

COPY cpu_burn.sh /cpu_burn.sh
RUN chmod +x /cpu_burn.sh

CMD ["/cpu_burn.sh"]
