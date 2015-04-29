"""
Some wheezy templates.
"""

docker = """\
@require(cidr, interface, containers)
domain ip {
    table nat {
        chain DOCKER;
        chain PREROUTING {
            policy ACCEPT;
            mod addrtype dst-type LOCAL jump DOCKER;
        }
        chain OUTPUT {
            policy ACCEPT;
            daddr ! 127.0.0.0/8 mod addrtype dst-type LOCAL jump DOCKER;
        }
        chain POSTROUTING {
            policy ACCEPT;
            saddr @cidr outerface ! @interface MASQUERADE;
        }
    }
    table filter {
        chain DOCKER;
        chain FORWARD {
            outerface @interface {
                jump DOCKER;
                mod conntrack ctstate (RELATED ESTABLISHED) ACCEPT;
            }
            interface @interface {
                outerface ! @interface ACCEPT;
                outerface @interface ACCEPT;
            }
        }
    }

    # container setup
    @for container in containers:
    # @container['Id']
    @(
        ip_address = container['NetworkSettings']['IPAddress']
        port_bindings = container['HostConfig']['PortBindings']

        # group into proto:port:(host:port)
        bindings = {}
        for port_proto, binds in port_bindings.iteritems():
            port, proto = port_proto.split("/")

            if proto not in bindings:
                bindings[proto] = {}

            if port not in bindings[proto]:
                bindings[proto][port] = []

            for bind in binds:
                bindings[proto][port].append((bind['HostIp'], bind['HostPort']))

    )
    table nat {
        chain POSTROUTING {
            # container setup
            @for proto, ports in bindings.iteritems():
            @for port, binds in ports.iteritems():
            saddr @ip_address/32 daddr @ip_address/32 protocol @proto {
                dport @port MASQUERADE;
            }
            @end
            @end
        }
        chain DOCKER {
            @for proto, ports in bindings.iteritems():
            @for port, binds in ports.iteritems():
            @for host_ip, host_port in binds:
            @{ host_ip and "daddr %s/32 " % host_ip or '' }interface ! @interface protocol tcp dport @host_port DNAT to @ip_address:@port;
            @end
            @end
            @end
        }
    }
    table filter {
        chain DOCKER {
            @for proto, ports in bindings.iteritems():
            daddr @ip_address/32 interface ! @interface outerface @interface protocol @proto {
            @for port, binds in ports.iteritems():
                dport @port ACCEPT;
            @end
            }
            @end
        }
    }
    @end
}
"""
