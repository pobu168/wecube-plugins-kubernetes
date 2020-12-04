# _ coding:utf-8 _*_

from __future__ import (absolute_import, division, print_function, unicode_literals)

from apps.common.kubernetes_auth_info import validate_cluster_auth
from apps.common.kubernetes_auth_info import validate_cluster_info
from core import local_exceptions as exception_common
from core import validation
from core.controller import BaseController
from lib.uuid_util import get_uuid
from .base import SecretApi


class SecretBaseController(BaseController):
    def not_null_keys(self):
        return ["kubernetes_url"]

    def before_handler(self, request, data, **kwargs):
        validate_cluster_auth(data)
        validation.not_allowed_null(data=data,
                                    keys=self.not_null_keys()
                                    )

        validation.validate_string("kubernetes_url", data["kubernetes_url"])
        validation.validate_string("kubernetes_token", data.get("kubernetes_token"))
        validation.validate_string("kubernetes_ca", data.get("kubernetes_ca"))
        validation.validate_string("apiversion", data.get("apiversion"))
        validation.validate_string("namespace", data.get("namespace"))
        validate_cluster_info(data["kubernetes_url"])


class SecretListController(SecretBaseController):
    name = "Secret"
    resource_describe = "Secret"
    allow_methods = ('POST',)
    resource = SecretApi()

    def response_templete(self, data):
        return []

    def main_response(self, request, data, **kwargs):
        return self.resource.list(kubernetes_url=data["kubernetes_url"],
                                  kubernetes_token=data.get("kubernetes_token"),
                                  kubernetes_ca=data.get("kubernetes_ca"),
                                  apiversion=data.get("apiversion"),
                                  namespace=data.get("namespace"),
                                  **kwargs)


class SecretAddController(SecretBaseController):
    name = "Secret"
    resource_describe = "Secret"
    allow_methods = ("POST",)
    resource = SecretApi()

    def not_null_keys(self):
        return ["kubernetes_url", "name", "server", "username", "password"]

    def response_templete(self, data):
        # todo detail secret create
        return {}

    def main_response(self, request, data, **kwargs):
        '''
        :param request:
        :param data:
        example:
        data = {
                    "kubernetes_url":"http://192.168.137.61:8080",
                    "kubernetes_token":null,
                    "kubernetes_ca":null,
                    "apiversion":"v1",
                    "labels": {"app": "mysql"},
                    "name":"mysql-Secret",
                    "replicas":1,
                    "image":"mysql:latest",
                    "containername":"mysql",
                    "containerlabels":{"app": "mysql"},
                    "containerports":"3306",
                    "selector":{"app": "mysql"},
                    "env":{"MYSQL_ROOT_PASSWORD":"qaz123456"},
                    "request_cpu":0.01,
                    "request_memory":128,
                    "limit_cpu":0.5,
                    "limit_memory":512
                }
        :param kwargs:
        :return:
        '''

        uuid = data.get("id", None) or get_uuid()

        kubernetes_url = data["kubernetes_url"]
        kubernetes_token = data.get("kubernetes_token")
        kubernetes_ca = data.get("kubernetes_ca")

        apiversion = data.get("apiversion", "v1")
        name = data["name"]
        server = data["server"]
        username = data["username"]
        password = data["password"]

        result = self.resource.create_docker_register(uuid=uuid,
                                                      kubernetes_url=kubernetes_url,
                                                      name=name,
                                                      server=server,
                                                      username=username,
                                                      password=password,
                                                      kubernetes_token=kubernetes_token,
                                                      kubernetes_ca=kubernetes_ca,
                                                      apiversion=apiversion,
                                                      namespace=data.get("namespace", "default")
                                                      )

        if result:
            result["id"] = uuid
        else:
            raise exception_common.ResoucrAddError("Secret 创建失败")

        return result


class SecretIdController(BaseController):
    name = "Secret.id"
    resource_describe = "Secret"
    allow_methods = ("POST",)
    resource = SecretApi()

    def not_null_keys(self):
        return ["kubernetes_url", "name"]

    def response_templete(self, data):
        # todo detail secret
        return {}

    def main_response(self, request, data, **kwargs):
        kubernetes_url = data["kubernetes_url"]
        kubernetes_token = data.get("kubernetes_token")
        kubernetes_ca = data.get("kubernetes_ca")
        name = data["name"]

        result = self.resource.show(name=name,
                                    kubernetes_url=kubernetes_url,
                                    kubernetes_token=kubernetes_token,
                                    kubernetes_ca=kubernetes_ca,
                                    apiversion=data.get("apiversion"),
                                    namespace=data.get("namespace", "default")
                                    )
        if not result:
            raise exception_common.ResourceNotFoundError()

        return result


class SecretDeleteController(SecretBaseController):
    name = "Secret"
    resource_describe = "Secret"
    allow_methods = ("POST",)
    resource = SecretApi()

    def not_null_keys(self):
        return ["kubernetes_url", "name"]

    def response_templete(self, data):
        return {"id": data.get("id"), "name": data["name"]}

    def main_response(self, request, data, **kwargs):
        name = data["name"]
        kubernetes_url = data["kubernetes_url"]
        kubernetes_token = data.get("kubernetes_token")
        kubernetes_ca = data.get("kubernetes_ca")

        result = self.resource.delete(name=name,
                                      kubernetes_url=kubernetes_url,
                                      kubernetes_token=kubernetes_token,
                                      kubernetes_ca=kubernetes_ca,
                                      apiversion=data.get("apiversion"),
                                      namespace=data.get("namespace", "default")
                                      )
        if not result:
            raise exception_common.ResourceNotFoundError()

        return result
