# _ coding:utf-8 _*_

from __future__ import (absolute_import, division, print_function, unicode_literals)

import json

from apps.background.lib.drivers.KubernetesDrivers import ServiceManager
from core.validation import validate_ipaddress
from lib.json_helper import format_json_dumps
from lib.logs import logger


class ServiceApi(object):
    def list(self, kubernetes_url, kubernetes_token=None,
             kubernetes_ca=None, apiversion=None,
             namespace="default", **kwargs):
        '''

        :param kubernetes_url:
        :param kubernetes_token:
        :param kubernetes_ca:
        :param apiversion:
        :param namespace:
        :param kwargs:
        :return:
        '''

        result = ServiceManager.list(url=kubernetes_url,
                                     token=kubernetes_token,
                                     cafile=kubernetes_ca,
                                     version=apiversion,
                                     namespace=namespace)
        return len(result), result

    def create(self, uuid, name,
               ports, kubernetes_url,
               type=None, kubernetes_token=None,
               kubernetes_ca=None, apiversion=None,
               labels=None, selector=None,
               clusterIP=None, namespace="default",
               **kwargs):
        '''
        :param uuid:
        :param name:
        :param nodeport:
        :param serviceport:
        :param containerport:
        :param kubernetes_url:
        :param type:
        :param kubernetes_token:
        :param kubernetes_ca:
        :param apiversion:
        :param labels:
        :param selector:
        :param clusterIP:
        :param namespace:
        :return:
        '''

        apiversion = apiversion or "v1"
        metadata = {"name": name}

        labels["uuid"] = uuid
        metadata["labels"] = labels

        type = type or "NodePort"

        spec_info = {"type": type, "selector": selector}

        spec_info["ports"] = ports

        if clusterIP:
            validate_ipaddress(clusterIP)
            spec_info["clusterIP"] = clusterIP

        create_data = {'apiVersion': apiversion,
                       'kind': 'Service',
                       'metadata': metadata,
                       'spec': spec_info
                       }

        logger.info(json.dumps(create_data))
        result = ServiceManager.create(uuid, createdata=create_data,
                                       url=kubernetes_url,
                                       token=kubernetes_token,
                                       cafile=kubernetes_ca,
                                       version=apiversion,
                                       namespace=namespace)
        return result

    def delete(self, name, kubernetes_url,
               kubernetes_token=None,
               kubernetes_ca=None, apiversion=None,
               namespace="default", **kwargs):
        '''

        :param name:
        :param kubernetes_url:
        :param kubernetes_token:
        :param kubernetes_ca:
        :param apiversion:
        :param namespace:
        :param kwargs:
        :return:
        '''

        return ServiceManager.delete(name, url=kubernetes_url,
                                     token=kubernetes_token,
                                     cafile=kubernetes_ca,
                                     version=apiversion,
                                     namespace=namespace)

    def show(self, name, kubernetes_url,
             kubernetes_token=None,
             kubernetes_ca=None, apiversion=None,
             namespace="default", **kwargs):
        '''
        :param name:
        :param kubernetes_url:
        :param kubernetes_token:
        :param kubernetes_ca:
        :param apiversion:
        :param namespace:
        :param kwargs:
        :return:
        '''

        result = ServiceManager.query(name, url=kubernetes_url,
                                      token=kubernetes_token,
                                      cafile=kubernetes_ca,
                                      version=apiversion,
                                      namespace=namespace)
        print(format_json_dumps(result))
        return result

    def _fetch_ports(self, ports):
        port_lists = []
        for port in ports:
            _port = "nodeport:%s&containerport:%s&serviceport:%s]" % (port["node_port"], port["target_port"], port["port"])
            port_lists.append(_port)

        return ",".join(port_lists)

    def detail(self, name, kubernetes_url,
               kubernetes_token=None,
               kubernetes_ca=None, apiversion=None,
               namespace="default", **kwargs):
        '''
        :param name:
        :param kubernetes_url:
        :param kubernetes_token:
        :param kubernetes_ca:
        :param apiversion:
        :param namespace:
        :param kwargs:
        :return:
        '''

        result = {}
        info = ServiceManager.query(name, url=kubernetes_url,
                                    token=kubernetes_token,
                                    cafile=kubernetes_ca,
                                    version=apiversion,
                                    namespace=namespace)
        if not info:
            return info

        result["cluster_ip"] = info["spec"]["cluster_ip"]
        _selector = info["spec"]["selector"]
        result["pod"] = _selector.get("app")
        result["type"] = info["spec"]["type"]
        ports = info["spec"]["ports"]
        result["ports"] = self._fetch_ports(ports)
        result["name"] = info["metadata"]["name"]
        result["created_time"] = info["metadata"]["creation_timestamp"]
        result["uid"] = info["metadata"]["uid"]
        result["labels"] = info["metadata"]["labels"]
        return result
