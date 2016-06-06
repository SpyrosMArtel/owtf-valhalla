from pprint import pprint
import time
import json

from django.views.generic import TemplateView
from django.http import HttpResponse
from django.core import serializers

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from web import serializers
from middleman import handler as middleman

from dockerutils import get_owtf_c, commands
# ThreadPool
from middleman.pool import TaskPool
# from random import choice
# import string
import Queue

class IndexTemplateView(TemplateView):
    template_name = 'index.html'


class ListAll(APIView):
    """Lists all the containers."""

    def get(self, request, format=None):

        image_status, images = get_owtf_c()

        if image_status:
            serializer = serializers.OwtfContainerSerializer(
                images,  # Get all containers
                many=True
            )

            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return HttpResponse('Failed to get _containers')


class Info(APIView):
    """Get info about a specific container."""

    def get(self, request, image, *args, **kwargs):

        image_status, image = get_owtf_c(image=image)

        if image_status:
            serializer = serializers.OwtfContainerSerializer(image)
            return Response(serializer.data, status=status.HTTP_200_OK)

        else:
            return HttpResponse('Failed!')


class BuildImage(APIView):
    """Build image"""

    def get(self, request, image, *args, **kwargs):

        image_status, image = get_owtf_c(image=image)

        if image_status:
            image.build_image()
            serializer = serializers.OwtfContainerSerializer(image)
            return Response(serializer.data, status=status.HTTP_200_OK)

        else:
            return HttpResponse('Failed!')


class RemoveImage(APIView):
    """Remove image"""

    def get(self, request, image, *args, **kwargs):

        image_status, image = get_owtf_c(image=image)

        if image_status:
            image.remove_image()
            serializer = serializers.OwtfContainerSerializer(image)
            return Response(serializer.data, status=status.HTTP_200_OK)

        else:
            return HttpResponse('Failed!')


class BuildContainer(APIView):
    """Build container"""

    def get(self, request, image, *args, **kwargs):

        image_status, image = get_owtf_c(image=image)

        if image_status:
            image.build_container()
            serializer = serializers.OwtfContainerSerializer(image)
            return Response(serializer.data, status=status.HTTP_200_OK)

        else:
            return HttpResponse('Failed!')


class RemoveContainer(APIView):
    """Remove container"""

    def get(self, request, image, *args, **kwargs):

        image_status, image = get_owtf_c(image=image)

        if image_status:
            image.remove_container()
            serializer = serializers.OwtfContainerSerializer(image)
            return Response(serializer.data, status=status.HTTP_200_OK)

        else:
            return HttpResponse('Failed!')


class Start(APIView):
    """Start container"""

    def get(self, request, image, *args, **kwargs):

        image_status, image = get_owtf_c(image=image)

        if image_status:
            image.start()
            serializer = serializers.OwtfContainerSerializer(image)
            return Response(serializer.data, status=status.HTTP_200_OK)

        else:
            return HttpResponse('Failed!')


class Stop(APIView):
    """Stop container"""

    def get(self, request, image, *args, **kwargs):

        image_status, image = get_owtf_c(image=image)

        if image_status:
            image.stop()
            serializer = serializers.OwtfContainerSerializer(image)
            return Response(serializer.data, status=status.HTTP_200_OK)

        else:
            return HttpResponse('Failed!')


class Commands(APIView):
    """Get a command and the pass it on to the associated container"""

    def get(self, request, *args, **kwargs):

        return Response(commands, status=status.HTTP_200_OK)


class Execute(APIView):
    """Get a command and the pass it on to the associated container"""

    def get(self, request, image, *args, **kwargs):

        image_status, image = get_owtf_c(image=image)

        if image_status:
            serializer = serializers.OwtfContainerSerializer(image)
            return Response(serializer.data, status=status.HTTP_200_OK)

        else:
            return HttpResponse('Failed!')

    def post(self, request, image, *args, **kwargs):

        image_status, image = get_owtf_c(image=image)

        if image_status:

            image.build_image()
            image.build_container()
            image.start()
            time.sleep(1)  # Wait for container to start

            request_data = serializers.CommandSerializer(data=request.data)
            if request_data.is_valid():
                result_queue = Queue.Queue(10)
                if not hasattr(self, 'pool'):
                    # Init a TaskPool with the desired number of threads
                    # currently it works with only one thread :(
                    self.pool = TaskPool(1)

                data = request_data.data

                # at this moment for testing we create a number of similar requests
                for i in range(5):
                    data['command'] = 'sleep 0.25s'
                    # data['command'] = 'echo ' + ''.join(choice(string.ascii_uppercase + string.digits) for _ in range(10))
                    self.pool.add_task(middleman.send_for_execution, image.ip_address, image.port, data)

                # image.results.append(result_queue.get() for _ in range(10))
                results = self.pool.wait()
                for result in results:
                    image.results.append(result)

                serializer = serializers.OwtfContainerSerializer(image)
                return Response(serializer.data, status=status.HTTP_200_OK)

                # image.results.append(middleman.send_for_execution(image.ip_address, image.port, request_data.data))
                # serializer = serializers.OwtfContainerSerializer(image)
                # return Response(serializer.data, status=status.HTTP_200_OK)

            pprint(request_data.errors)
            return HttpResponse('Command is not valid!')
        else:
            return HttpResponse('Failed!')


class BuildAll(APIView):
    """Build all images and containers. This may take some time!"""

    def get(self, request):

        image_status, image = get_owtf_c()
        print(image)

        for c in image:
            c.build_image()
            c.build_container()

        image_status, image = get_owtf_c()

        if image_status:
            serializer = serializers.OwtfContainerSerializer(image, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)

        else:
            return HttpResponse('Failed to build all!')


class RebuildAll(APIView):
    """Rebuild all images and containers, may take some time!"""

    def get(self, request):

        image_status, image = get_owtf_c()
        print(image)

        for c in image:
            c.stop()
            c.remove_container()
            c.remove_image()
            c.build_image()
            c.build_container()

        image_status, image = get_owtf_c()

        if image_status:
            serializer = serializers.OwtfContainerSerializer(image, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)

        else:
            return HttpResponse('Failed to build all!')


class StopAll(APIView):
    """Stop and remove all containers"""

    def get(self, request):

        image_status, image = get_owtf_c()
        print(image)

        for c in image:
            c.stop()
            c.remove_container()

        image_status, image = get_owtf_c()

        if image_status:
            serializer = serializers.OwtfContainerSerializer(image, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)

        else:
            return HttpResponse('Failed to stop all!')
