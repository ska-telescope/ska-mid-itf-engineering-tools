"""Read all information about Tango devices in a Kubernetes cluster."""

import json
import logging
import socket

import yaml

from ska_mid_itf_engineering_tools.k8s_info.get_k8s_info import KubernetesControl
from ska_mid_itf_engineering_tools.tango_control.tango_control import TangoControl


class TangoControlSkao(TangoControl):
    """Read Tango devices running in a Kubernetes cluster."""

    def __init__(self, logger: logging.Logger):
        super().__init__(logger)

    def check_tango(
        self,
        tango_fqdn: str,
        quiet_mode: bool,
        tango_port: int = 10000,
    ) -> int:
        """
        Check Tango host address.

        :param tango_fqdn: fully qualified domain name
        :param quiet_mode: flag to suppress extra output
        :param tango_port: port number
        :return: error condition
        """
        self.logger.info("Check Tango host %s:%d", tango_fqdn, tango_port)
        try:
            tango_addr = socket.gethostbyname_ex(tango_fqdn)
            tango_ip = tango_addr[2][0]
        except socket.gaierror as e:
            self.logger.error("Could not read address %s : %s" % (tango_fqdn, e))
            return 1
        if not quiet_mode:
            print(f"TANGO_HOST={tango_fqdn}:{tango_port}")
            print(f"TANGO_HOST={tango_ip}:{tango_port}")
        return 0

    def get_namespaces_list(self) -> list:
        """
        Read namespaces in Kubernetes cluster.

        :return: list with devices
        """
        k8s = KubernetesControl(self.logger)
        ns_list = k8s.get_namespaces_list()
        self.logger.info("Read %d namespaces", len(ns_list))
        return ns_list

    def get_namespaces_dict(self) -> dict:
        """
        Read namespaces in Kubernetes cluster.

        :return: dictionary with devices
        """
        k8s = KubernetesControl(self.logger)
        ns_dict = k8s.get_namespaces_dict()
        self.logger.info("Read %d namespaces", len(ns_dict))
        return ns_dict

    def show_namespaces(self, output_file: str | None, fmt: str) -> None:
        """
        Display namespaces in Kubernetes cluster.

        :param output_file: output file name
        :param fmt: output format
        """
        if fmt == "json":
            ns_dict = self.get_namespaces_dict()
            if output_file is not None:
                self.logger.info("Write output file %s", output_file)
                with open(output_file, "w") as outf:
                    outf.write(json.dumps(ns_dict, indent=4))
            else:
                print(json.dumps(ns_dict, indent=4))
        elif fmt == "yaml":
            ns_dict = self.get_namespaces_dict()
            if output_file is not None:
                self.logger.info("Write output file %s", output_file)
                with open(output_file, "w") as outf:
                    outf.write(yaml.dump(ns_dict))
            else:
                print(yaml.dump(ns_dict))
        else:
            ns_list = self.get_namespaces_list()
            print(f"Namespaces : {len(ns_list)}")
            for ns_name in ns_list:
                print(f"\t{ns_name}")

    def get_pods_dict(self, ns_name: str | None) -> dict:
        """
        Read pods in Kubernetes namespace.

        :param ns_name: namespace name
        :param logger: logging handle
        :return: dictionary with devices
        """
        k8s = KubernetesControl(self.logger)
        pods_dict = k8s.get_pods(ns_name, None)
        self.logger.info("Read %d pods", len(pods_dict))
        return pods_dict

    def print_pods(self, ns_name: str | None, quiet_mode: bool) -> None:  # noqa: C901
        """
        Display pods in Kubernetes namespace.

        :param ns_name: namespace name
        :param quiet_mode: flag to suppress extra output
        """
        if ns_name is None:
            self.logger.error("K8S namespace not specified")
            return
        k8s = KubernetesControl(self.logger)
        pods_dict = self.get_pods_dict(ns_name)
        print(f"Pods : {len(pods_dict)}")
        for pod_name in pods_dict:
            print(f"{pod_name}")
            if not quiet_mode:
                resps = k8s.exec_command(ns_name, pod_name, ["ps", "-ef"])
                if not resps:
                    pass
                elif "\n" in resps:
                    for resp in resps.split("\n"):
                        self.logger.debug("Got '%s'", resp)
                        if not resp:
                            pass
                        elif resp[-6:] == "ps -ef":
                            pass
                        elif resp[0:3] == "UID":
                            pass
                        elif resp[0:3] == "PID":
                            pass
                        # elif "nginx" in resp:
                        #     pass
                        elif resp[0:5] in ("tango", "root ", "mysql") or resp[0:3] == "100":
                            respl = resp.split()
                            print(f"\t* {respl[0]:8} {' '.join(respl[7:])}")
                        else:
                            print(f"\t  {resp}")
                else:
                    print(f"\t- {resps}")

    def get_pods_json(self, ns_name: str | None, quiet_mode: bool) -> dict:
        """
        Read pods in Kubernetes namespace.

        :param ns_name: namespace name
        :param quiet_mode: print progress bars
        :return: dictionary with pod information
        """
        pods: dict = {}
        pod_exec: list = ["ps", "-ef"]
        if ns_name is None:
            self.logger.error("K8S namespace not specified")
            return pods
        k8s = KubernetesControl(self.logger)
        self.logger.debug("Read pods running in namespace %s", ns_name)
        pods_list = k8s.get_pods(ns_name, None)
        self.logger.info("Found %d pods running in namespace %s", len(pods_list), ns_name)
        for pod_name in pods_list:
            self.logger.info("Read processes running in pod %s", pod_name)
            resps = k8s.exec_command(ns_name, pod_name, pod_exec)
            pods[pod_name] = []
            if not resps:
                pass
            elif "\n" in resps:
                for resp in resps.split("\n"):
                    if not resp:
                        pass
                    elif resp[-6:] == "ps -ef":
                        pass
                    elif resp[0:3] == "UID":
                        pass
                    elif resp[0:3] == "PID":
                        pass
                    # elif "nginx" in resp:
                    #     pass
                    else:
                        pods[pod_name].append(resp)
            else:
                pods[pod_name].append(resps)
        return pods

    def show_pods(
        self, ns_name: str | None, quiet_mode: bool, output_file: str | None, fmt: str | None
    ) -> None:
        """
        Display pods in Kubernetes namespace.

        :param ns_name: namespace name
        :param quiet_mode: flag to suppress progress bar etc.
        :param output_file: output file name
        :param fmt: output format
        """
        if fmt == "json":
            pods = self.get_pods_json(ns_name, quiet_mode)
            if output_file is not None:
                self.logger.info("Write output file %s", output_file)
                with open(output_file, "w") as outf:
                    outf.write(json.dumps(pods, indent=4))
            else:
                print(json.dumps(pods, indent=4))
        elif fmt == "yaml":
            pods = self.get_pods_json(ns_name, quiet_mode)
            if output_file is not None:
                self.logger.info("Write output file %s", output_file)
                with open(output_file, "w") as outf:
                    outf.write(yaml.dump(pods))
            else:
                print(yaml.dump(pods))
        elif fmt == "txt":
            self.print_pods(ns_name, quiet_mode)
        else:
            # show_pods(ns_name, quiet_mode, output_file, fmt)
            self.logger.warning("Output format %s not supported", fmt)
            pass
