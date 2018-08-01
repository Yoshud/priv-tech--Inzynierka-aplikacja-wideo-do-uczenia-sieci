from django.views.generic import View
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.http import Http404, HttpResponseServerError
from mainServer.models import *
from mainServer.skryptyEtapy.helpersMethod import *
from wsgiref.util import FileWrapper
from django.http import HttpResponse
from scipy.interpolate import interp1d
# from copy import copy
import json
import os
from functools import reduce
from django.core.exceptions import MultipleObjectsReturned
from django.core.exceptions import ObjectDoesNotExist
from time import sleep
import numpy as np

@method_decorator(csrf_exempt, name='dispatch')
class ReturnMoviesToProcess(View):
    def post(self, request, **kwargs):
        movies = Film.objects \
                     .filter(status__status__in=["Do przetworzenia"])[:5]
        moviesDict = [self.addMovieToMoviesDict(movie) for movie in movies]
        return JsonResponse({
            "movies": moviesDict,
        })

    def addMovieToMoviesDict(self, movie,
                             statusToRemove=StatusFilmu.objects.get_or_create(status="Do przetworzenia")[0],
                             statusToAdd=StatusFilmu.objects.get_or_create(status="W trakcie przetwarzania")[0]):
        movie.status.remove(statusToRemove)
        movie.status.add(statusToAdd)
        return {
            "path": movie.sciezka,
            "movieName": movie.nazwa,
            "id": movie.pk,
            "pathToSave": movie.sesja.folderZObrazami.sciezka,
        }


@method_decorator(csrf_exempt, name='dispatch')
class MovieProcessed(View):
    def post(self, request, **kwargs):
        data = json.loads(request.read().decode('utf-8').replace("'", "\""))
        movieId = data.get("movieId", False)
        frames = data["frames"]
        try:
            self.addToProcessedMovies(Film.objects.get(pk=movieId), frames)
        except:
            raise HttpResponseServerError
        return JsonResponse({"ok": True})

    def addToProcessedMovies(self, movie, frames,
                             statusToRemove=StatusFilmu.objects.get_or_create(status="W trakcie przetwarzania")[0],
                             statusToAdd=StatusFilmu.objects.get_or_create(status="Przetworzono")[0]):
        movie.status.remove(statusToRemove)
        movie.status.add(statusToAdd)
        for frameInfo in frames:
            frame = Klatka(sciezka=frameInfo["path"], nr=frameInfo["nr"], film=movie)
            frame.save()
        print(movie.nazwa)


@method_decorator(csrf_exempt, name='dispatch')
class GetNextMovie(View):
    def post(self, request, **kwargs):
        data = json.loads(request.read().decode('utf-8'))
        try:
            sessionId = data["sessionId"]
        except:
            raise Http404
        try:
            previousMovieId = data["previousMovieId"]

            previousMovie = Film.objects.get(pk=previousMovieId)
            statusToAdd = StatusFilmu.objects.get_or_create(status="Przypisano punkty")[0]
            removeMultipleStatuses(previousMovie, ["W trakcie obslugi", "Przetworzono"])
            previousMovie.status.add(statusToAdd)
            previousMovie.save()
        except KeyError:
            pass
        except:
            raise HttpResponseServerError
        finally:
            try:
                nextMovie = Film.objects \
                    .filter(sesja__pk=sessionId, status__status__in=["Przetworzono"]) \
                    .order_by("data")[0]
                statusToAdd = StatusFilmu.objects.get_or_create(status="W trakcie obslugi")[0]
                nextMovie.status.add(statusToAdd)
            except IndexError:
                movieCount = Film.objects \
                    .filter(sesja__pk=sessionId, status__status__in=["W trakcie przetwarzania"]).count()
                if movieCount:
                    return JsonResponse({"count": movieCount})
                else:
                    raise Http404
        return JsonResponse({
            "movieId": nextMovie.pk,
            "framesCount": nextMovie.iloscKlatek,
            "fps": nextMovie.FPS,
            "name": nextMovie.nazwa,
            "x": nextMovie.rozmiarX,
            "y": nextMovie.rozmiarY,
        })


@method_decorator(csrf_exempt, name='dispatch')
class GetFrame(View):
    def post(self, request, **kwargs):
        data = json.loads(request.read().decode('utf-8'))
        movieId = data.get("movieId")
        frameNr = data.get("frameNr")
        imagePath = Klatka.objects.get(film__pk=movieId, nr=frameNr).sciezka
        wrapper = FileWrapper(open(os.path.abspath(imagePath), 'rb'))
        response = HttpResponse(wrapper, content_type='image/jpg')
        response['Content-Disposition'] = 'attachment; imageName=%s' % os.path.basename(imagePath)
        response['Content-Length'] = os.path.getsize(imagePath)
        return response


@method_decorator(csrf_exempt, name='dispatch')
class FramePosition(View):

    def get(self, request, **kwargs):
        data = json.loads(request.read().decode('utf-8'))
        try:
            movieId = data["movieId"]
            frameNr = data["frameNr"]
            positionObjects = PozycjaPunktu.objects.filter(klatka__film__pk=movieId, klatka__nr=frameNr)
        except TypeError:
            try:
                frameId = data.get("frameId")
                positionObjects = PozycjaPunktu.objects.filter(klatka__pk=frameId)
            except:
                raise Http404
        finally:
            return JsonResponse(self.positionsAsDict(positionObjects))

    def post(self, request, **kwargs):
        try:
            data = json.loads(request.read().decode('utf-8'))
            frameId = data["frameId"]
            position = data["position"]
            x = position["x"]
            y = position["y"]
            frameObject = Klatka.objects.get(pk=frameId)
        except:
            raise Http404
        try:
            status = data["status"]
        except TypeError:
            status = "Dodane uzytkownik"
        except:
            raise Http404
        finally:
            statusObject = StatusPozycji.objects.get_or_create(status=status)[0]
            position = PozycjaPunktu.objects.create(klatka=frameObject, status=statusObject, pozycjaX=x, pozycjaY=y) # sprawdzac czy nie wystepuje
            if status == endPositionStatus:
                self.addInterpolationPosition(frameObject)
            return JsonResponse({"positionId": position.pk})

    def positionsAsDict(self, positions):
        if positions is None:
            return None
        if len(positions) > 0:
            positionsArray = [{
                                  "x": position.pozycjaX,
                                  "y": position.pozycjaY,
                                  "status": position.status.status,
                                  "id": position.pk,
                              } if position else None
                              for position in positions]
            return {"positions": positionsArray,
                    "frameId": positions[-1].klatka.pk,
                    }
        else:
            return {}

    def xsAndYsFromDicts(self, dictions):
        if dictions is None:
            return None
        return zip(*[(dictElement["x"], dictElement["y"]) if dictElement else (None, None)
                for dictElement in dictions['positions']])

    def positionsXYInfo(self, positionObjects):
        positionDicts = self.positionsAsDict(positionObjects)

        def toReduceSplitByEndStatus(ret, positionDict):  # second index its cache
            ret[1].append({
                "x": positionDict["x"],
                "y": positionDict["y"]
            })
            if positionDict["status"] == endPositionStatus:  # or len(ret[1]) == 0
                ret[0].append(ret[1][:])
                ret[1] = []

        splitedByEndStatus = list(reduce(toReduceSplitByEndStatus, positionDicts, ([], [])))[0]
        xs, ys = [self.xsAndYsFromDicts(dictions) for dictions in splitedByEndStatus]
        return xs, ys

    def findLastFrameWithEndStatusOrNone(self, frame):
        # frame = Klatka.objects.get(pk=frameId)
        movieId = frame.film.pk
        ordererFramesWithEndStatus = Klatka.objects \
            .filter(film__pk=movieId, nr__lt=frame.nr, pozycja__status__status__in=[endPositionStatus, ]) \
            .order_by("nr")
        try:
            return ordererFramesWithEndStatus[-1]
        except:
            try:
                return ordererFramesWithEndStatus[0]
            except:
                return None

    def findStartFrame(self, frame):
        firstEndFrame = self.findLastFrameWithEndStatusOrNone(frame)
        if firstEndFrame:
            startFrame = Klatka.objects.get(film=firstEndFrame.film, nr=(firstEndFrame.nr + 1))
        else:
            startFrame = Klatka.objects.get(film=frame.film, nr=0)
        return startFrame

    def findAllFramesFromStartToEnd(self, frame):
        # frame = Klatka.objects.get(pk=frameId)
        startFrame = self.findStartFrame(frame)
        return Klatka.objects.filter(film=startFrame.film, nr__gte=startFrame.nr, nr__lte=frame.nr)

    def userPositionsXsYsInfo(self, framesFromStartToEnd):
        def getUserPositionOrNone(frame):
            try:
                return PozycjaPunktu.objects.get(klatka=frame,
                                                 status__status__in=[userPositionStatus, endPositionStatus])
            except ObjectDoesNotExist:
                return None
            # except:
            #     raise HttpResponseServerError

        positions = [
            getUserPositionOrNone(frame)
            for frame in framesFromStartToEnd]

        return self.xsAndYsFromDicts(self.positionsAsDict(positions))

    def interpolate(self, xs):
        itsXs = [[it, x] for it, x in enumerate(xs)]
        itsXs = [el for el in itsXs if el[1] is not None]
        its, xsNotNone = list(zip(*itsXs))
        f = interp1d(its, xsNotNone, kind='quadratic', bounds_error=False, fill_value='extrapolate')
        return f(range(len(xs)))

    def addInterpolationPosition(self, frame):
        frames = self.findAllFramesFromStartToEnd(frame)
        # out = self.userPositionsXsYsInfo(frames)
        xs, ys = self.userPositionsXsYsInfo(frames)
        interpolatedXs = self.interpolate(xs)
        interpolatedYs = self.interpolate(ys)
        for x, y, frame in zip(interpolatedXs, interpolatedYs, frames):
            status = StatusPozycji.objects.get_or_create(status=interpolatedPositonStatus)[0]
            newPosition = PozycjaPunktu.objects.create(
                pozycjaX=x,
                pozycjaY=y,
                status=status,
                klatka=frame)
            sleep(0.01)  # prevent from locking database in sqlite


@method_decorator(csrf_exempt, name='dispatch')
class DeletePosition(View):
    def post(self, request, **kwargs):
        try:
            data = json.loads(request.read().decode('utf-8'))
            positionId = data["positionId"]
            positionObject = PozycjaPunktu.objects.get(pk=positionId)
            deleted = positionObject.delete()
            if deleted.count() != 0:
                raise Http404
        except:
            raise Http404

        return JsonResponse({"ok": "ok"})
