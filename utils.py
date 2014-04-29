import datetime
import io
import babelfish
import collections
from flask import url_for
import guessit
import operator

__author__ = 'alexandreferreira'
import os
from subliminal import (__version__, cache_region, MutexLock, provider_manager, Video, Episode, Movie, scan_video,
    download_best_subtitles, ProviderPool)

BASE_DIR = os.path.dirname(__file__)
STATIC_ROOT = os.path.join(BASE_DIR, "static")

def search_for_subtitle(nome_arquivo, languages):
    BASE_DIR = os.path.dirname(os.path.dirname(__file__))
    BASE_DIR = os.path.join("..", BASE_DIR)
    BASE_DIR = os.path.join(BASE_DIR, 'cli.dbm')
    try:
        languages = babelfish.Language.fromietf(languages)
    except babelfish.Error:
        pass

    video = Video.fromguess(nome_arquivo, guessit.guess_file_info(nome_arquivo))

    subtitle_downloaded = get_video_urls({video}, {languages} )
    infos = save_subtitles(subtitle_downloaded)
    return infos


def get_video_urls(videos, languages, providers=None, provider_configs=None, min_score=0,
                            hearing_impaired=False, single=False):
    """Download the best subtitles for `videos` with the given `languages` using the specified `providers`

    :param videos: videos to download subtitles for
    :type videos: set of :class:`~subliminal.video.Video`
    :param languages: languages of subtitles to download
    :type languages: set of :class:`babelfish.Language`
    :param providers: providers to use for the search, if not all
    :type providers: list of string or None
    :param provider_configs: configuration for providers
    :type provider_configs: dict of provider name => provider constructor kwargs or None
    :param int min_score: minimum score for subtitles to download
    :param bool hearing_impaired: download hearing impaired subtitles
    :param bool single: do not download for videos with an undetermined subtitle language detected

    """
    downloaded_subtitles = collections.defaultdict(list)
    with ProviderPool(providers, provider_configs) as pp:
        for video in videos:
            # filter
            if single and babelfish.Language('und') in video.subtitle_languages:

                continue

            # list

            video_subtitles = pp.list_subtitles(video, languages)


            # download
            downloaded_languages = set()
            for subtitle, score in sorted([(s, s.compute_score(video)) for s in video_subtitles],
                                          key=operator.itemgetter(1), reverse=True):
                if score < min_score:

                    break
                if subtitle.hearing_impaired != hearing_impaired:

                    continue
                if subtitle.language in downloaded_languages:

                    continue

                if pp.download_subtitle(subtitle):
                    downloaded_languages.add(subtitle.language)
                    downloaded_subtitles[video].append(subtitle)
                if single or downloaded_languages == languages:

                    break
    return downloaded_subtitles

def save_subtitles(subtitles, single=False, directory=None, encoding="utf-8"):
    """Save subtitles on disk next to the video or in a specific folder if `folder_path` is specified

    :param bool single: download with .srt extension if ``True``, add language identifier otherwise
    :param directory: path to directory where to save the subtitles, if any
    :type directory: string or None
    :param encoding: encoding for the subtitles or ``None`` to use the original encoding
    :type encoding: string or None
    :return list of subtitles
    :type list of :class:``dict``

    """
    list_subtitles = []
    for video, video_subtitles in subtitles.items():
        saved_languages = set()
        for video_subtitle in video_subtitles:
            if video_subtitle.content is None:
                continue
            if video_subtitle.language in saved_languages:
                continue
            file_name = get_subtitle_path(os.path.splitext(video.name)[0], None if single else video_subtitle.language)
            subtitle_path = os.path.join(get_path_saved_subtitle(video_subtitle.provider_name), file_name)
            if encoding is None:
                with io.open(subtitle_path, 'wb') as f:
                    f.write(video_subtitle.content)
            else:
                with io.open(subtitle_path, 'w', encoding=encoding) as f:
                    f.write(video_subtitle.text)
            saved_languages.add(video_subtitle.language)
            list_subtitles.append({'provider': video_subtitle.provider_name, 'file_name': file_name,
                                   'video_name': video.name,
                                   'url_file': "http://freesubs.herokuapp.com"+
                                               url_for('static', filename=video_subtitle.provider_name+"/"+file_name) })
            if single:
                break
    return list_subtitles

def get_path_saved_subtitle(provider):

    path = os.path.join(STATIC_ROOT, provider)
    if not os.path.exists(path): os.makedirs(path)
    return path

def get_subtitle_path(video_path, language=None):
    """Create the subtitle path from the given `video_path` and `language`

    :param string video_path: path to the video
    :param language: language of the subtitle to put in the path
    :type language: :class:`babelfish.Language` or None
    :return: path of the subtitle
    :rtype: string

    """
    subtitle_path = video_path
    if language is not None:
        try:
            return subtitle_path + '.%s.%s' % (language.alpha2, 'srt')
        except babelfish.LanguageConvertError:
            return subtitle_path + '.%s.%s' % (language.alpha3, 'srt')
    return subtitle_path + '.srt'
