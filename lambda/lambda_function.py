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

        ### Fun stuff for display backgorund###
        if util.supports_display(handler_input):
            background_img = Image(
                sources=[ImageInstance(
                    url=util.get_image(
                        ht=1024, wd=600, label=item["abbreviation"]))])

            response_builder.add_directive(
                RenderTemplateDirective(
                    ListTemplate1(
                        token="Hear-o",
                        back_button=BackButtonBehavior.HIDDEN,
                        background_image=background_img,
                        title="Hear-o",
                        list_items=item_list)))
        ###################################################################

        handler_input.response_builder.speak(util.speak_in_english(data.WELCOME_MESSAGE)).ask(
            util.speak_in_english(data.WELCOME_MESSAGE))
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
        # topic = handler_input.request_envelope.request.intent.slots['generalanswer'].value
        # question = util.speak_in_english("Great! Shall we revise on " + topic + "?")

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
        ################ for full functionality, we need something to match the topic of users choice to one in database  ####
        return (is_intent_name("GeneralAnswerIntent")(handler_input) and
                attr.get("state") == "TOPIC")

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        attr = handler_input.attributes_manager.session_attributes
        attr["state"] = "STARTQUESTIONS"
        attr["question_number"] = 0
        # attr["question_number"]+=1
        attr["wrong_answer_number"] = 0

        passage = util.choose_passage(0)  # hard coded passage number, should be a function of topic chosen. -> french
        question = data.QUESTION_LIST[0]  # hard coded question number -> french
        message = util.in_english(data.LISTENING_PASSAGE_MESSAGE)  # -> english
        next_message = util.in_english(data.LISTENING_PASSAGE_QUESTION_START)
        final_message = '<speak>' + message + ' <break time="1s"/>' + passage + ' <break time="1s"/>' + next_message + ' <break time="1s"/>' + question + '</speak>'

        # message = '<speak>This is working! <voice name="Celine"><lang xml:lang="fr-FR"> Oui oui!</lang></voice></speak>'

        # handler_input.response_builder.speak(message).ask(message)
        response_builder = handler_input.response_builder
        response_builder.speak(final_message)
        response_builder.ask(final_message)
        attr["last_said"] = question
        return response_builder.response


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
        attr["last_said"] = question
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

        if user_answer == actual_answer:
            attr["wrong_answer_number"] = 0
            if (attr["question_number"]) == len(data.QUESTION_LIST) - 1:
                attr['state'] = 'ANSWERINFRENCH_INTRO'
                response = response = '<speak>Très bien! <voice name="Amy"><lang xml:lang="en-GB">Shall we move on to the next section of this lesson? </lang></voice>' + '</speak>'
            else:
                attr["question_number"] += 1
                response = '<speak>Très bien! <voice name="Amy"><lang xml:lang="en-GB">Let us move on to the next question. </lang></voice>' + \
                           data.QUESTION_LIST[attr["question_number"]] + '</speak>'
        else:
            if attr.get("wrong_answer_number") == 0:
                attr["wrong_answer_number"] += 1
            else:
                attr["wrong_answer_number"] = 0
                if (attr["question_number"]) == len(data.QUESTION_LIST):
                    response = '<speak>Pas vrai. <voice name="Amy"><lang xml:lang="en-GB"> The correct answer is: </lang></voice>' + \
                               data.ANSWER_LIST[attr[
                                   "question_number"]] + ' <voice name="Amy"><lang xml:lang="en-GB">Shall we move on to the next section of this lesson? </lang></voice>' + '</speak>'
                    attr['state'] = 'ANSWERINFRENCH_INTRO'
                else:
                    response = '<speak>Pas vrai. <voice name="Amy"><lang xml:lang="en-GB"> The correct answer is: </lang></voice>' + \
                               data.ANSWER_LIST[attr[
                                   "question_number"]] + ' <voice name="Amy"><lang xml:lang="en-GB">The next question is: </lang></voice>' + \
                               data.QUESTION_LIST[attr["question_number"] + 1] + '</speak>'
                    attr["question_number"] += 1

        response_builder = handler_input.response_builder
        response_builder.speak(response)
        response_builder.ask(response)
        attr["last_said"] = response
        return response_builder.response


class RepeatInEnglishIntentHandler(AbstractRequestHandler):
    "Ask Alexa to repeat what was last said in english"

    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return is_intent_name("InEnglishIntent")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        attr = handler_input.attributes_manager.session_attributes
        last_said = attr.get("last_said")  ## or whatever we want to translate

        translator = Translator()
        translator.translate(last_said, dest="en")

        last_said_translated = util.speak_in_english(translated.text)

        response_builder = handler_input.response_builder
        response_builder.speak(last_said_translated)
        response_builder.ask(last_said_translated)

        return response_builder.response


class ProceedToAnswerInFrenchIntentHandler(AbstractRequestHandler):
    """Handler for proceeding to passage reading, and then questioning"""

    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        attr = handler_input.attributes_manager.session_attributes
        ################ for full functionality, we need something to match the topic of users choice to one in database  ####
        return (is_intent_name("GeneralAnswerIntent")(handler_input) and
                attr.get("state") == "ANSWERINFRENCH_INTRO")

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response

        attr = handler_input.attributes_manager.session_attributes
        attr["state"] = "ANSWERINFRENCH"
        attr["sayinfrench_number"] = 0
        attr["wrong_answer_number"] = 0

        question = data.sayinfrench_QUESTION_LIST[0]

        final_message = util.speak_in_english(
            'Okay, can you say the French equivalent of the following phrases? Remember to use the proper articles. ' + str(
                question))

        response_builder = handler_input.response_builder
        response_builder.speak(final_message)
        response_builder.ask(final_message)
        return response_builder.response


class AnswerinFrenchIntentHandler(AbstractRequestHandler):
    "Answer Alexa's question"

    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        attr = handler_input.attributes_manager.session_attributes
        return (is_intent_name("GeneralAnswerIntent")(handler_input) and
                attr.get("state") == "ANSWERINFRENCH")

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        attr = handler_input.attributes_manager.session_attributes
        sayinfrench_number = attr.get("sayinfrench_number")
        user_answer = handler_input.request_envelope.request.intent.slots['generalanswer'].value
        actual_answer = data.sayinfrench_ANSWER_LIST[sayinfrench_number]
        response = "Ce n'est pas vrai, please try again!"

        if user_answer == actual_answer:
            attr["wrong_answer_number"] = 0

            if (attr["sayinfrench_number"]) == len(data.sayinfrench_QUESTION_LIST) - 1:
                attr['state'] = 'END'
                response = response = '<speak>Très bien! <voice name="Amy"><lang xml:lang="en-GB">Great Job and see you again! </lang></voice>' + '</speak>'
            else:
                attr["sayinfrench_number"] += 1
                response = '<speak>Très bien! <voice name="Amy"><lang xml:lang="en-GB">Let us move on to the next question. </lang></voice>' + \
                           data.sayinfrench_QUESTION_LIST[attr["sayinfrench_number"]] + '</speak>'
        else:
            if attr.get("wrong_answer_number") == 0:
                attr["wrong_answer_number"] += 1
            else:
                attr["wrong_answer_number"] = 0

                if (attr["sayinfrench_number"]) == len(data.sayinfrench_QUESTION_LIST) - 1:
                    response = '<speak>Pas vrai. <voice name="Amy"><lang xml:lang="en-GB"> The correct answer is: </lang></voice>' + \
                               data.sayinfrench_ANSWER_LIST[attr[
                                   "sayinfrench_number"]] + ' <voice name="Amy"><lang xml:lang="en-GB">Great job and see you again! </lang></voice>' + '</speak>'
                    attr['state'] = 'END'
                else:
                    response = '<speak>Pas vrai. <voice name="Amy"><lang xml:lang="en-GB"> The correct answer is: </lang></voice>' + \
                               data.sayinfrench_ANSWER_LIST[attr[
                                   "sayinfrench_number"]] + ' <voice name="Amy"><lang xml:lang="en-GB">The next question is: </lang></voice>' + \
                               data.sayinfrench_QUESTION_LIST[attr["sayinfrench_number"] + 1] + '</speak>'
                    attr["sayinfrench_number"] += 1

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
sb.add_request_handler(AnswerinFrenchIntentHandler())
# sb.add_request_handler(QuizAnswerHandler())
# sb.add_request_handler(QuizAnswerElementSelectedHandler())
sb.add_request_handler(RepeatHandler())
sb.add_request_handler(HelpIntentHandler())
sb.add_request_handler(ExitIntentHandler())
sb.add_request_handler(SessionEndedRequestHandler())
sb.add_request_handler(FallbackIntentHandler())
sb.add_request_handler(RepeatInEnglishIntentHandler())
sb.add_request_handler(ProceedToAnswerInFrenchIntentHandler())

# Add exception handler to the skill.
sb.add_exception_handler(CatchAllExceptionHandler())

# Add response interceptor to the skill.
sb.add_global_response_interceptor(CacheResponseForRepeatInterceptor())
sb.add_global_request_interceptor(RequestLogger())
sb.add_global_response_interceptor(ResponseLogger())

# Expose the lambda handler to register in AWS Lambda.
lambda_handler = sb.lambda_handler()
