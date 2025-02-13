from . import BaseInlineMarkup


class FeedbackMarkup(BaseInlineMarkup):
    view_feedback = ("📖 View feedbacks", "view_feedback")
    leave_feedback = ("✍🏼 Leave feedback", "leave_feedback")


class CancelActionInlineMarkup(BaseInlineMarkup):
    cancel = ("❌ Cancel", "cancel")


class AnonymousMarkup(BaseInlineMarkup):
    not_anonymous = ("🙉 Not Anonymous", "anonymous:false")
    anonymous = ("🙈 Anonymous", "anonymous:true")
    cancel = CancelActionInlineMarkup.cancel
