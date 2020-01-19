# -*- coding: utf-8 -*-

# IMPORTANT: Please note that this template uses Display Directives,
# Display Interface for your skill should be enabled through the Amazon
# developer console
# See this screen shot - https://alexa.design/enabledisplay

import json
import logging
from googletrans import Translator

from ask_sdk_core.skill_builder import SkillBuilder
from ask_sdk_core.handler_input import HandlerInput
from ask_sdk_core.serialize import DefaultSerializer
from ask_sdk_core.dispatch_components import (
    AbstractRequestHandler, AbstractExceptionHandler,
    AbstractResponseInterceptor, AbstractRequestInterceptor)
from ask_sdk_core.utils import is_intent_name, is_request_type
from ask_sdk_core.response_helper import (
    get_plain_text_content, get_rich_text_content)

from ask_sdk_model.interfaces.display import (
    ImageInstance, Image, RenderTemplateDirective, ListTemplate1,
    BackButtonBehavior, ListItem, BodyTemplate2, BodyTemplate1)
from ask_sdk_model import ui, Response

from alexa import data, util

# Skill Builder object
sb = SkillBuilder()

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


# Request Handler classes
class LaunchRequestHandler(AbstractRequestHandler):
    """Handler for skill launch."""

    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return is_request_type("LaunchRequest")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        logger.info("In LaunchRequestHandler")
        attr = handler_input.attributes_manager.session_attributes
        attr["state"] = "WELCOME"
        handler_input.response_builder.speak(util.speak_in_english(data.WELCOME_MESSAGE)).ask(
            util.speak_in_english(data.HELP_MESSAGE))
        return handler_input.response_builder.response


class SessionEndedRequestHandler(AbstractRequestHandler):
    """Handler for skill session end."""

    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return is_request_type("SessionEndedRequest")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        logger.info("In SessionEndedRequestHandler")
        print("Session ended with reason: {}".format(
            handler_input.request_envelope))
        return handler_input.response_builder.response


class HelpIntentHandler(AbstractRequestHandler):
    """Handler for help intent."""

    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return is_intent_name("AMAZON.HelpIntent")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        logger.info("In HelpIntentHandler")
        handler_input.attributes_manager.session_attributes = {}
        # Resetting session

        handler_input.response_builder.speak(
            util.speak_in_english(data.HELP_MESSAGE)).ask(data.HELP_MESSAGE)
        return handler_input.response_builder.response


class ExitIntentHandler(AbstractRequestHandler):
    """Single Handler for Cancel, Stop and Pause intents."""

    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return (is_intent_name("AMAZON.CancelIntent")(handler_input) or
                is_intent_name("AMAZON.StopIntent")(handler_input) or
                is_intent_name("AMAZON.PauseIntent")(handler_input))

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        logger.info("In ExitIntentHandler")
        handler_input.response_builder.speak(
            util.speak_in_english(data.EXIT_SKILL_MESSAGE)).set_should_end_session(True)
        return handler_input.response_builder.response


# ----------------------- START OF OUR INTENTS --------------------------------------- #

class AnswerToWelcomeIntentHandler(AbstractRequestHandler):
    """Handler for asking about topic"""

    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        attr = handler_input.attributes_manager.session_attributes
        return (is_intent_name("GeneralAnswerIntent")(handler_input) and
                attr.get("state") == "WELCOME")

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        attr = handler_input.attributes_manager.session_attributes
        attr["state"] = "TOPIC"
        question = util.speak_in_english(data.REVISE_TOPIC_MESSAGE)
        response_builder = handler_input.response_builder
        response_builder.speak(question)
        response_builder.ask(question)
        return response_builder.response


class ProceedToPassageIntentHandler(AbstractRequestHandler):
    """Handler for proceeding to passage reading, and then questioning"""

    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        attr = handler_input.attributes_manager.session_attributes
        return (is_intent_name("GeneralAnswerIntent")(handler_input) and
                attr.get("state") == "TOPIC")

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        attr = handler_input.attributes_manager.session_attributes
        attr["state"] = "STARTQUESTIONS"
        attr["question_number"] = 0

        passage = util.choose_passage(0)  # hard coded passage number, should be a function of topic chosen.
        message = util.speak_in_english(LISTENING_PASSAGE_MESSAGE)+passage+util.speak_in_english(LISTENING_PASSAGE_QUESTION_START)

        response_builder = handler_input.response_builder
        response_builder.speak(message)
        response_builder.ask(message)
        return response_builder.response


"""
class NextQuestionIntentHandler(AbstractRequestHandler):

    def can_handle(self, handler_input):
"""


class RepeatQuestionIntentHandler(AbstractRequestHandler):
    "Ask Alexa to repeat the question"

    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return is_intent_name("RepeatQuestionIntent")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        attr = handler_input.attributes_manager.session_attributes
        question_number = attr.get("question_number")
        question = data.QUESTION_LIST[question_number]

        response_builder = handler_input.response_builder
        response_builder.speak(question)
        response_builder.ask(question)

        return response_builder.response


class AnswerQuestionIntentHandler(AbstractRequestHandler):
    "Answer Alexa's question"

    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        attr = handler_input.attributes_manager.session_attributes
        return (is_intent_name("GeneralAnswerIntent")(handler_input) and
                attr.get("state") == "STARTQUESTIONS")

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        attr = handler_input.attributes_manager.session_attributes
        question_number = attr.get("question_number")
        user_answer = handler_input.request_envelope.request.intent.slots['generalanswer'].value
        actual_answer = data.ANSWER_LIST[question_number]
        response = "Ce n'est pas vrai, please try again!"
        # if user_answer == actual answer:
        #    attr["question_number"] += 1
        # I STOPPED HERE
        if user_answer == actual_answer:
            response = "Très bien! Shall we move on to the next question?"

        response_builder = handler_input.response_builder
        response_builder.speak(response)
        response_builder.ask(response)

        return response_builder.response


# -----------------------------------AMAZON INBUILT STUFF------------------------------------------ #
# ------------------------------------------------------------------------------------------------- #

class RepeatHandler(AbstractRequestHandler):
    """Handler for repeating the response to the user."""

    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return is_intent_name("AMAZON.RepeatIntent")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        logger.info("In RepeatHandler")
        attr = handler_input.attributes_manager.session_attributes
        response_builder = handler_input.response_builder
        if "recent_response" in attr:
            cached_response_str = json.dumps(attr["recent_response"])
            cached_response = DefaultSerializer().deserialize(
                cached_response_str, Response)
            return cached_response
        else:
            response_builder.speak(util.speak_in_english(data.FALLBACK_ANSWER)).ask(data.HELP_MESSAGE)

            return response_builder.response


class FallbackIntentHandler(AbstractRequestHandler):
    """Handler for handling fallback intent.

     2018-May-01: AMAZON.FallackIntent is only currently available in
     en-US locale. This handler will not be triggered except in that
     locale, so it can be safely deployed for any locale."""

    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return is_intent_name("AMAZON.FallbackIntent")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        logger.info("In FallbackIntentHandler")
        handler_input.response_builder.speak(
            data.FALLBACK_ANSWER).ask(data.HELP_MESSAGE)

        return handler_input.response_builder.response


# Interceptor classes
class CacheResponseForRepeatInterceptor(AbstractResponseInterceptor):
    """Cache the response sent to the user in session.

    The interceptor is used to cache the handler response that is
    being sent to the user. This can be used to repeat the response
    back to the user, in case a RepeatIntent is being used and the
    skill developer wants to repeat the same information back to
    the user.
    """

    def process(self, handler_input, response):
        # type: (HandlerInput, Response) -> None
        session_attr = handler_input.attributes_manager.session_attributes
        session_attr["recent_response"] = response


# Exception Handler classes
class CatchAllExceptionHandler(AbstractExceptionHandler):
    """Catch All Exception handler.

    This handler catches all kinds of exceptions and prints
    the stack trace on AWS Cloudwatch with the request envelope."""

    def can_handle(self, handler_input, exception):
        # type: (HandlerInput, Exception) -> bool
        return True

    def handle(self, handler_input, exception):
        # type: (HandlerInput, Exception) -> Response
        logger.error(exception, exc_info=True)

        speech = "Sorry, there was some problem. Please try again!!"
        handler_input.response_builder.speak(speech).ask(speech)

        return handler_input.response_builder.response


# Request and Response Loggers
class RequestLogger(AbstractRequestInterceptor):
    """Log the request envelope."""

    def process(self, handler_input):
        # type: (HandlerInput) -> None
        logger.info("Request Envelope: {}".format(
            handler_input.request_envelope))


class ResponseLogger(AbstractResponseInterceptor):
    """Log the response envelope."""

    def process(self, handler_input, response):
        # type: (HandlerInput, Response) -> None
        logger.info("Response: {}".format(response))


# Add all request handlers to the skill.
sb.add_request_handler(LaunchRequestHandler())
# sb.add_request_handler(QuizHandler())
# sb.add_request_handler(DefinitionHandler())
sb.add_request_handler(RepeatQuestionIntentHandler())
sb.add_request_handler(AnswerToWelcomeIntentHandler())
sb.add_request_handler(ProceedToPassageIntentHandler())
sb.add_request_handler(AnswerQuestionIntentHandler())
# sb.add_request_handler(QuizAnswerHandler())
# sb.add_request_handler(QuizAnswerElementSelectedHandler())
sb.add_request_handler(RepeatHandler())
sb.add_request_handler(HelpIntentHandler())
sb.add_request_handler(ExitIntentHandler())
sb.add_request_handler(SessionEndedRequestHandler())
sb.add_request_handler(FallbackIntentHandler())

# Add exception handler to the skill.
sb.add_exception_handler(CatchAllExceptionHandler())

# Add response interceptor to the skill.
sb.add_global_response_interceptor(CacheResponseForRepeatInterceptor())
sb.add_global_request_interceptor(RequestLogger())
sb.add_global_response_interceptor(ResponseLogger())

# Expose the lambda handler to register in AWS Lambda.
lambda_handler = sb.lambda_handler()
